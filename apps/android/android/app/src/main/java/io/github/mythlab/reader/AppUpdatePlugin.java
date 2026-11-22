package io.github.mythlab.reader;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;

import androidx.core.content.FileProvider;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.MessageDigest;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * In-app updates for builds that are not on Google Play: {@code getInfo} (installed version), {@code download}
 * (an https APK into the cache, checked against the SHA-256 the manifest promised) and {@code install} (hands the
 * file to the system installer). Android itself refuses an APK that is not signed with the installed app's key, so
 * a wrong file can never replace the app; the checks here only keep the user from a pointless install prompt.
 *
 * Events: {@code progress} {loaded, total} while downloading.
 */
@CapacitorPlugin(name = "AppUpdate")
public class AppUpdatePlugin extends Plugin {
    private static final String DIR = "shared";
    private static final String FILE = "update.apk";
    private static final String MIME = "application/vnd.android.package-archive";
    private static final long MAX_BYTES = 200L << 20;

    private final AtomicBoolean busy = new AtomicBoolean(false);

    @Override
    public void load() {
        // after a successful update the downloaded file is stale: do not leave 10+ MB in the cache
        try {
            File f = apkFile();
            if (f.exists()) {
                PackageInfo pi = archiveInfo(f);
                if (pi == null || versionCodeOf(pi) <= installedCode()) f.delete();
            }
        } catch (RuntimeException ignored) {
            // best effort
        }
    }

    private File apkFile() {
        File dir = new File(getContext().getCacheDir(), DIR);
        if (!dir.exists()) dir.mkdirs();
        return new File(dir, FILE);
    }

    private PackageInfo installed() throws PackageManager.NameNotFoundException {
        Context c = getContext();
        return c.getPackageManager().getPackageInfo(c.getPackageName(), 0);
    }

    private static long versionCodeOf(PackageInfo pi) {
        return Build.VERSION.SDK_INT >= 28 ? pi.getLongVersionCode() : pi.versionCode;
    }

    private long installedCode() {
        try {
            return versionCodeOf(installed());
        } catch (PackageManager.NameNotFoundException e) {
            return 0;
        }
    }

    private PackageInfo archiveInfo(File f) {
        return getContext().getPackageManager().getPackageArchiveInfo(f.getAbsolutePath(), 0);
    }

    private boolean canInstall() {
        return Build.VERSION.SDK_INT < 26 || getContext().getPackageManager().canRequestPackageInstalls();
    }

    @PluginMethod
    public void getInfo(PluginCall call) {
        try {
            PackageInfo pi = installed();
            JSObject o = new JSObject();
            o.put("versionName", pi.versionName == null ? "" : pi.versionName);
            o.put("versionCode", versionCodeOf(pi));
            o.put("canInstall", canInstall());
            call.resolve(o);
        } catch (PackageManager.NameNotFoundException e) {
            call.reject("no package info");
        }
    }

    /**
     * Reads the small update manifest natively: static files on the server carry no CORS headers, so the WebView
     * (origin https://localhost) could not fetch it. Returns {text}; the page parses and validates it.
     */
    @PluginMethod
    public void fetchManifest(PluginCall call) {
        final String url = call.getString("url", "");
        if (url == null || !url.startsWith("https://")) {
            call.reject("https only");
            return;
        }
        getBridge().execute(() -> {
            HttpURLConnection c = null;
            try {
                c = (HttpURLConnection) new URL(url).openConnection();
                c.setConnectTimeout(10000);
                c.setReadTimeout(15000);
                c.setUseCaches(false);
                c.setRequestProperty("Cache-Control", "no-cache");
                int code = c.getResponseCode();
                if (code != 200) {
                    call.reject("HTTP " + code);
                    return;
                }
                java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
                try (InputStream in = c.getInputStream()) {
                    byte[] buf = new byte[4096];
                    int n;
                    while ((n = in.read(buf)) > 0) {
                        bos.write(buf, 0, n);
                        if (bos.size() > 64 * 1024) throw new IOException("manifest too large");
                    }
                }
                JSObject o = new JSObject();
                o.put("text", bos.toString("UTF-8"));
                call.resolve(o);
            } catch (Exception e) {
                call.reject(e.getMessage() == null ? "network" : e.getMessage());
            } finally {
                if (c != null) c.disconnect();
            }
        });
    }

    @PluginMethod
    public void download(PluginCall call) {
        final String url = call.getString("url", "");
        final String want = call.getString("sha256", "");
        if (url == null || !url.startsWith("https://")) {
            call.reject("https only");
            return;
        }
        if (want == null || !want.matches("(?i)[0-9a-f]{64}")) {
            call.reject("sha256 required");
            return;
        }
        if (!busy.compareAndSet(false, true)) {
            call.reject("busy");
            return;
        }
        getBridge().execute(() -> {
            File part = new File(apkFile().getParentFile(), FILE + ".part");
            try {
                long size = fetch(url, part);
                String got = sha256(part);
                if (!got.equalsIgnoreCase(want)) {
                    part.delete();
                    call.reject("checksum");
                    return;
                }
                File dst = apkFile();
                if (dst.exists() && !dst.delete()) throw new IOException("cannot replace old file");
                if (!part.renameTo(dst)) throw new IOException("cannot move file");
                JSObject o = new JSObject();
                o.put("size", size);
                call.resolve(o);
            } catch (Exception e) {
                part.delete();
                call.reject(e.getMessage() == null ? "download failed" : e.getMessage());
            } finally {
                busy.set(false);
            }
        });
    }

    private long fetch(String url, File dst) throws IOException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(15000);
        c.setReadTimeout(30000);
        c.setInstanceFollowRedirects(true);
        try {
            int code = c.getResponseCode();
            if (code != 200) throw new IOException("HTTP " + code);
            long total = c.getContentLengthLong();
            if (total > MAX_BYTES) throw new IOException("file too large");
            long loaded = 0;
            long lastEmit = 0;
            try (InputStream in = c.getInputStream(); OutputStream out = new FileOutputStream(dst)) {
                byte[] buf = new byte[64 * 1024];
                int n;
                while ((n = in.read(buf)) > 0) {
                    out.write(buf, 0, n);
                    loaded += n;
                    if (loaded > MAX_BYTES) throw new IOException("file too large");
                    long now = System.currentTimeMillis();
                    if (now - lastEmit > 250) {
                        lastEmit = now;
                        JSObject o = new JSObject();
                        o.put("loaded", loaded);
                        o.put("total", total);
                        notifyListeners("progress", o);
                    }
                }
            }
            if (total >= 0 && loaded != total) throw new IOException("incomplete download");
            JSObject done = new JSObject();
            done.put("loaded", loaded);
            done.put("total", loaded);
            notifyListeners("progress", done);
            return loaded;
        } finally {
            c.disconnect();
        }
    }

    private static String sha256(File f) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        try (InputStream in = new java.io.FileInputStream(f)) {
            byte[] buf = new byte[64 * 1024];
            int n;
            while ((n = in.read(buf)) > 0) md.update(buf, 0, n);
        }
        StringBuilder sb = new StringBuilder(64);
        for (byte b : md.digest()) sb.append(String.format(Locale.ROOT, "%02x", b));
        return sb.toString();
    }

    @PluginMethod
    public void install(PluginCall call) {
        File f = apkFile();
        if (!f.isFile()) {
            call.reject("no downloaded update");
            return;
        }
        PackageInfo pi = archiveInfo(f);
        if (pi == null || !getContext().getPackageName().equals(pi.packageName)) {
            f.delete();
            call.reject("not an update for this app");
            return;
        }
        if (versionCodeOf(pi) <= installedCode()) {
            f.delete();
            call.reject("already up to date");
            return;
        }
        if (getActivity() == null) {
            call.reject("no activity");
            return;
        }
        if (!canInstall()) {
            // the user has to allow "install unknown apps" for MythLab once; send them to that switch
            Intent s = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + getContext().getPackageName()));
            s.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getActivity().startActivity(s);
            call.reject("permission");
            return;
        }
        try {
            Uri uri = FileProvider.getUriForFile(getContext(), getContext().getPackageName() + ".fileprovider", f);
            Intent i = new Intent(Intent.ACTION_VIEW).setDataAndType(uri, MIME);
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            getActivity().startActivity(i);
            call.resolve();
        } catch (RuntimeException e) {
            call.reject("cannot open the installer");
        }
    }
}
