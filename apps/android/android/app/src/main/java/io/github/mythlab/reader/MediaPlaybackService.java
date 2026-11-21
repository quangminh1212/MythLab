package io.github.mythlab.reader;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.media.MediaMetadata;
import android.media.session.MediaSession;
import android.media.session.PlaybackState;
import android.os.Build;
import android.os.IBinder;
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

    private MediaSession session;
    private PowerManager.WakeLock wakeLock;
    private String title = "MythLab Truyện";
    private String artist = "";
    private boolean playing = true;
    private boolean foreground = false;

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();
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
        setWakeLock(false);
        if (session != null) {
            session.setActive(false);
            session.release();
            session = null;
        }
        super.onDestroy();
    }
}
