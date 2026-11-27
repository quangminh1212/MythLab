package io.github.mythlab.reader;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.PowerManager;
import android.provider.Settings;
import android.webkit.WebView;

import com.getcapacitor.JSObject;
import com.getcapacitor.PermissionState;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.Permission;
import com.getcapacitor.annotation.PermissionCallback;

/** JS bridge for {@link MediaPlaybackService}: start / update / stop and an 'action' event. */
@CapacitorPlugin(
    name = "MediaPlayback",
    permissions = { @Permission(alias = "notifications", strings = { Manifest.permission.POST_NOTIFICATIONS }) }
)
public class MediaPlaybackPlugin extends Plugin {
    private static MediaPlaybackPlugin instance;
    private volatile boolean playing = false;

    @Override
    public void load() {
        instance = this;
    }

    @Override
    protected void handleOnDestroy() {
        if (instance == this) instance = null;
    }

    /** Called by the service on notification / lock-screen buttons. */
    static void emit(String action) {
        MediaPlaybackPlugin p = instance;
        if (p == null) return;
        JSObject o = new JSObject();
        o.put("action", action);
        p.notifyListeners("action", o, true);
    }

    private void send(String action, PluginCall call) {
        Context c = getContext();
        Intent i = new Intent(c, MediaPlaybackService.class).setAction(action);
        if (call != null) {
            String t = call.getString("title");
            String a = call.getString("artist");
            if (t != null) i.putExtra("title", t);
            if (a != null) i.putExtra("artist", a);
            if (call.hasOption("playing")) i.putExtra("playing", Boolean.TRUE.equals(call.getBoolean("playing", true)));
        }
        // already running in the foreground (the usual case while speaking): no new start request, which Android 12+
        // can refuse once the app is in the background
        if (!MediaPlaybackService.ACT_START.equals(action) && MediaPlaybackService.deliver(i)) return;
        try {
            if (Build.VERSION.SDK_INT >= 26 && !MediaPlaybackService.ACT_STOP.equals(action)) c.startForegroundService(i);
            else c.startService(i);
        } catch (RuntimeException e) {
            // e.g. started from the background on Android 12+: skip, the web player keeps working
        }
    }

    @PluginMethod
    public void start(PluginCall call) {
        playing = true;
        if (Build.VERSION.SDK_INT >= 33 && getPermissionState("notifications") != PermissionState.GRANTED) {
            requestPermissionForAlias("notifications", call, "afterPermission");
            return;
        }
        send(MediaPlaybackService.ACT_START, call);
        call.resolve();
    }

    @PermissionCallback
    private void afterPermission(PluginCall call) {
        // started either way: the service still keeps the process alive when notifications are denied
        send(MediaPlaybackService.ACT_START, call);
        call.resolve();
    }

    @PluginMethod
    public void update(PluginCall call) {
        playing = Boolean.TRUE.equals(call.getBoolean("playing", true));
        send(MediaPlaybackService.ACT_UPDATE, call);
        call.resolve();
    }

    @PluginMethod
    public void stop(PluginCall call) {
        playing = false;
        send(MediaPlaybackService.ACT_STOP, null);
        call.resolve();
    }

    /** True when the system lets the app run without battery restrictions (so OEM task killers leave playback alone). */
    @PluginMethod
    public void batteryStatus(PluginCall call) {
        JSObject o = new JSObject();
        boolean ignoring = true;
        if (Build.VERSION.SDK_INT >= 23) {
            PowerManager pm = (PowerManager) getContext().getSystemService(Context.POWER_SERVICE);
            ignoring = pm == null || pm.isIgnoringBatteryOptimizations(getContext().getPackageName());
        }
        o.put("unrestricted", ignoring);
        call.resolve(o);
    }

    /** Opens the system battery-optimisation list (no extra permission needed), falling back to the app details page. */
    @PluginMethod
    public void openBatterySettings(PluginCall call) {
        Context c = getContext();
        Intent i = new Intent(Build.VERSION.SDK_INT >= 23 ? Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS : Settings.ACTION_SETTINGS)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        try {
            c.startActivity(i);
        } catch (RuntimeException e) {
            try {
                c.startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + c.getPackageName())).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            } catch (RuntimeException e2) {
                call.reject("no settings screen");
                return;
            }
        }
        call.resolve();
    }

    // Keep the WebView's JS timers running while the app is in the background and speech is on.
    @Override
    protected void handleOnPause() {
        keepAlive();
    }

    @Override
    protected void handleOnStop() {
        keepAlive();
    }

    private void keepAlive() {
        if (!playing || getBridge() == null) return;
        final WebView w = getBridge().getWebView();
        if (w != null) w.post(w::resumeTimers);
    }
}
