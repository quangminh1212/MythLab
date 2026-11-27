package io.github.mythlab.reader;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.ServiceInfo;
import android.media.AudioManager;
import android.media.MediaMetadata;
import android.media.session.MediaSession;
import android.media.session.PlaybackState;
import android.os.Build;
import android.net.wifi.WifiManager;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;

/**
 * Foreground service (mediaPlayback) that keeps the app process alive while the web player speaks:
 * partial wake lock, MediaSession (lock screen / headset / notification controls) and an ongoing notification.
 * Buttons are forwarded to JS through {@link MediaPlaybackPlugin#emit}.
 */
public class MediaPlaybackService extends Service {
    static final String ACT_START = "io.github.mythlab.reader.MEDIA_START";
    static final String ACT_UPDATE = "io.github.mythlab.reader.MEDIA_UPDATE";
    static final String ACT_STOP = "io.github.mythlab.reader.MEDIA_STOP";
    static final String ACT_PLAY = "io.github.mythlab.reader.MEDIA_PLAY";
    static final String ACT_PAUSE = "io.github.mythlab.reader.MEDIA_PAUSE";
    static final String ACT_NEXT = "io.github.mythlab.reader.MEDIA_NEXT";
    static final String ACT_PREV = "io.github.mythlab.reader.MEDIA_PREV";
    private static final String CHANNEL = "mythlab_playback";
    private static final int NOTIF_ID = 4711;

    /** The running service (main thread writes), so the plugin can update it without a new start request. */
    private static volatile MediaPlaybackService instance;

    private MediaSession session;
    private PowerManager.WakeLock wakeLock;
    private WifiManager.WifiLock wifiLock;
    private BroadcastReceiver noisy;
    private String title = "MythLab Truyện";
    private String artist = "";
    private boolean playing = true;
    private boolean foreground = false;

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    /**
     * Hands an intent to the service when it already runs in the foreground. Calling startForegroundService from the
     * background (screen off, next chapter) can be refused on Android 12+, a direct call never is.
     */
    static boolean deliver(final Intent i) {
        final MediaPlaybackService s = instance;
        if (s == null || !s.foreground) return false;
        new Handler(Looper.getMainLooper()).post(() -> {
            if (instance == s && s.session != null) s.onStartCommand(i, 0, 0);
        });
        return true;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
        NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26 && nm != null) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "Phát truyện", NotificationManager.IMPORTANCE_LOW);
            ch.setShowBadge(false);
            nm.createNotificationChannel(ch);
        }
        session = new MediaSession(this, "MythLabPlayback");
        session.setCallback(new MediaSession.Callback() {
            @Override public void onPlay() { MediaPlaybackPlugin.emit("play"); }
            @Override public void onPause() { MediaPlaybackPlugin.emit("pause"); }
            @Override public void onSkipToNext() { MediaPlaybackPlugin.emit("next"); }
            @Override public void onSkipToPrevious() { MediaPlaybackPlugin.emit("previous"); }
        });
        session.setActive(true);
        // headphones unplugged / Bluetooth lost: pause instead of blasting the speaker
        noisy = new BroadcastReceiver() {
            @Override public void onReceive(Context context, Intent intent) {
                if (AudioManager.ACTION_AUDIO_BECOMING_NOISY.equals(intent.getAction())) MediaPlaybackPlugin.emit("pause");
            }
        };
        IntentFilter f = new IntentFilter(AudioManager.ACTION_AUDIO_BECOMING_NOISY);
        try {
            if (Build.VERSION.SDK_INT >= 33) registerReceiver(noisy, f, Context.RECEIVER_NOT_EXPORTED);
            else registerReceiver(noisy, f);
        } catch (RuntimeException e) {
            noisy = null;
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String a = intent != null ? intent.getAction() : null;
        if (a == null) a = ACT_START;
        switch (a) {
            case ACT_STOP:
                shutdown(startId);
                return START_NOT_STICKY;
            case ACT_PLAY: MediaPlaybackPlugin.emit("play"); return START_NOT_STICKY;
            case ACT_PAUSE: MediaPlaybackPlugin.emit("pause"); return START_NOT_STICKY;
            case ACT_NEXT: MediaPlaybackPlugin.emit("next"); return START_NOT_STICKY;
            case ACT_PREV: MediaPlaybackPlugin.emit("previous"); return START_NOT_STICKY;
            default:
                break;
        }
        if (intent != null) {
            if (intent.hasExtra("title")) title = intent.getStringExtra("title");
            if (intent.hasExtra("artist")) artist = intent.getStringExtra("artist");
            if (intent.hasExtra("playing")) playing = intent.getBooleanExtra("playing", true);
            else if (ACT_START.equals(a)) playing = true;
        }
        render();
        return START_NOT_STICKY;
    }

    private void render() {
        MediaMetadata.Builder mb = new MediaMetadata.Builder();
        mb.putString(MediaMetadata.METADATA_KEY_TITLE, title == null ? "" : title);
        mb.putString(MediaMetadata.METADATA_KEY_ARTIST, artist == null ? "" : artist);
        session.setMetadata(mb.build());
        long actions = PlaybackState.ACTION_PLAY | PlaybackState.ACTION_PAUSE | PlaybackState.ACTION_PLAY_PAUSE
                | PlaybackState.ACTION_SKIP_TO_NEXT | PlaybackState.ACTION_SKIP_TO_PREVIOUS;
        session.setPlaybackState(new PlaybackState.Builder()
                .setActions(actions)
                .setState(playing ? PlaybackState.STATE_PLAYING : PlaybackState.STATE_PAUSED, PlaybackState.PLAYBACK_POSITION_UNKNOWN, 1f)
                .build());
        setWakeLock(playing);

        Notification n = buildNotification();
        if (!foreground) {
            try {
                if (Build.VERSION.SDK_INT >= 29) {
                    startForeground(NOTIF_ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK);
                } else {
                    startForeground(NOTIF_ID, n);
                }
                foreground = true;
            } catch (RuntimeException e) {
                stopSelf();
            }
        } else {
            NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm != null) nm.notify(NOTIF_ID, n);
        }
    }

    private PendingIntent action(String act, int code) {
        Intent i = new Intent(this, MediaPlaybackService.class).setAction(act);
        int f = PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= 23 ? PendingIntent.FLAG_IMMUTABLE : 0);
        // the service is already in the foreground, so a plain service PendingIntent is allowed
        return PendingIntent.getService(this, code, i, f);
    }

    private Notification buildNotification() {
        Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(this, CHANNEL) : new Notification.Builder(this);
        Intent open = new Intent(this, MainActivity.class).setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        int f = PendingIntent.FLAG_UPDATE_CURRENT | (Build.VERSION.SDK_INT >= 23 ? PendingIntent.FLAG_IMMUTABLE : 0);
        b.setSmallIcon(android.R.drawable.ic_media_play)
                .setContentTitle(title)
                .setContentText(artist)
                .setContentIntent(PendingIntent.getActivity(this, 0, open, f))
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setVisibility(Notification.VISIBILITY_PUBLIC)
                .addAction(new Notification.Action.Builder(android.R.drawable.ic_media_previous, "Trước", action(ACT_PREV, 1)).build());
        if (playing) b.addAction(new Notification.Action.Builder(android.R.drawable.ic_media_pause, "Tạm dừng", action(ACT_PAUSE, 2)).build());
        else b.addAction(new Notification.Action.Builder(android.R.drawable.ic_media_play, "Phát", action(ACT_PLAY, 3)).build());
        b.addAction(new Notification.Action.Builder(android.R.drawable.ic_media_next, "Sau", action(ACT_NEXT, 4)).build());
        b.setStyle(new Notification.MediaStyle().setMediaSession(session.getSessionToken()).setShowActionsInCompactView(0, 1, 2));
        return b.build();
    }

    private void setWakeLock(boolean on) {
        try {
            if (on) {
                if (wakeLock == null) {
                    PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
                    wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MythLab:playback");
                    wakeLock.setReferenceCounted(false);
                }
                if (!wakeLock.isHeld()) wakeLock.acquire(6 * 60 * 60 * 1000L); // safety timeout: 6 h
            } else if (wakeLock != null && wakeLock.isHeld()) {
                wakeLock.release();
            }
        } catch (RuntimeException ignored) {
            // no wake lock
        }
        setWifiLock(on);
    }

    /** Keeps Wi-Fi awake while speaking so the next chapter / progress sync works with the screen off. */
    @SuppressWarnings("deprecation")
    private void setWifiLock(boolean on) {
        try {
            if (on) {
                if (wifiLock == null) {
                    WifiManager wm = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
                    if (wm == null) return;
                    wifiLock = wm.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "MythLab:playback");
                    wifiLock.setReferenceCounted(false);
                }
                if (!wifiLock.isHeld()) wifiLock.acquire();
            } else if (wifiLock != null && wifiLock.isHeld()) {
                wifiLock.release();
            }
        } catch (RuntimeException ignored) {
            // no Wi-Fi lock
        }
    }

    private void shutdown(int startId) {
        setWakeLock(false);
        foreground = false;
        stopForeground(true);
        if (startId > 0) stopSelf(startId); else stopSelf();
    }

    @Override
    public void onTaskRemoved(Intent rootIntent) {
        shutdown(0);
    }

    @Override
    public void onDestroy() {
        if (instance == this) instance = null;
        setWakeLock(false);
        if (noisy != null) {
            try {
                unregisterReceiver(noisy);
            } catch (RuntimeException ignored) {
                // not registered
            }
            noisy = null;
        }
        if (session != null) {
            session.setActive(false);
            session.release();
            session = null;
        }
        super.onDestroy();
    }
}
