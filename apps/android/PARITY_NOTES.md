# Android app parity notes (Capacitor WebView vs desktop web)

Audited: capacitor.config.json, sync-web.mjs, package.json plugins, MainActivity, MediaPlayback / AppUpdate plugins, and the web code paths that branch on `Capacitor` / `isNative()`.

## Already fine
- Back button (core/backnav.ts), Google sign-in (auth-native.ts + capgo social-login), in-app update (AppUpdate plugin), status/nav bar colours (ThemeBars plugin).
- Listening in background / screen off: MediaPlayback foreground service (mediaPlayback type, wake lock, notification with play/pause/next/prev) wired by player/native-media.ts; KeepAwake plugin keeps the screen on while speaking; native TTS engine.
- Storage: IndexedDB, Cache API, Web Locks and `navigator.storage.persist()` all work under `https://localhost`; the service worker is deliberately off in the app (pwa.ts).
- Hover-only UI: none found that the app depends on. Picture-in-picture "Cửa sổ nhỏ" needs Document PiP (desktop Chromium only) and is hidden when unsupported; that is expected, not a gap.

## Gap fixed in web/ (needs no native change to be usable)
- Backup export: a blob `<a download>` click does nothing in the WebView. New `web/src/app/core/export-file.ts` (`saveTextFile`) tries Capacitor Filesystem+Share, a native `FileShare` plugin, Web Share with a file, then the link download; in the app with none of those it returns `manual` and Settings shows the JSON in a textarea with a Copy button. A "Dán nội dung sao lưu…" box was added next to Import so the copied text can be restored without a file.
- Copy story link: `copyText()` falls back to a hidden textarea + `execCommand('copy')` when the async Clipboard API is denied in the WebView.

## Native TODO (to get a real file export in the app)
Pick one:
1. `npm i @capacitor/filesystem @capacitor/share` in apps/android, then `npx cap sync android`. The web side uses them automatically (writes to CACHE, opens the share sheet so the user can save to Drive/Files). `res/xml/file_paths.xml` may need `<cache-path name="cache_root" path="." />` so the Share plugin's FileProvider can serve the cache file (the app's own provider only exposes `shared/`; the Share plugin registers its own, check its README).
2. Or add a small `FileShare` plugin (`@PluginMethod share(name, text, mime)`: write to `getCacheDir()/shared/<name>`, then `Intent.ACTION_SEND` with `FileProvider.getUriForFile(ctx, ctx.getPackageName()+".fileprovider", file)`, `FLAG_GRANT_READ_URI_PERMISSION`, wrapped in `Intent.createChooser`). `shared/` is already exposed by file_paths.xml. Register in MainActivity next to AppUpdatePlugin. The web code calls `Capacitor.Plugins.FileShare.share({name, text, mime})`.

## Not verified (no device)
`adb` is not installed on this machine, so nothing was tested on a device/emulator. To check on a real device: soft keyboard vs the reader search / chapter jump inputs (Android 15 edge-to-edge may need `adjustResize` or the Capacitor Keyboard plugin if inputs are covered), lock-screen controls, and the file chooser for "Nhập từ tệp…".

## Screen-off audio
Audit (code review only, no device): the chain is foreground service `MediaPlaybackService` (type mediaPlayback, manifest + FOREGROUND_SERVICE_MEDIA_PLAYBACK, PARTIAL_WAKE_LOCK, MediaSession, ongoing notification on channel `mythlab_playback`) driven by `player/native-media.ts`. Capacitor `KeepRunning` defaults to true, so `webView.onPause()/pauseTimers()` is never called, and `setMediaPlaybackRequiresUserGesture(false)` is set by Capacitor's Bridge, so `<audio>.play()` of the next Piper clip works with the screen off. Piper/Kokoro clips are WAV blobs played through one `<audio>` element (no AudioContext, so no suspend handling is needed); the next chunk is synthesised in the Worker while the current one plays.

Gaps found and fixed:
- Native TTS was driven one sentence at a time from JS (`await speak()` per piece, QUEUE_FLUSH each). With the WebView throttled the voice paused between sentences. `engines.ts` now queues all sentences of a chunk (QUEUE_ADD) and also the next chunk (announced by `prefetch`), and follows the queue; a changed speed/voice/chunk flushes it. Stop rejects pending chunks (the plugin never answers utterances a stop dropped).
- Service updates used `startForegroundService` even while already running, which Android 12+ may refuse from the background (next chapter with screen off, title change). `MediaPlaybackService.deliver()` now hands updates to the running service directly.
- No pause when headphones are unplugged (native TTS would play on the speaker): `ACTION_AUDIO_BECOMING_NOISY` now emits `pause`.
- Wi-Fi could sleep in the background (next chapter fetch, progress sync): a Wi-Fi lock is held while playing.
- Battery restrictions (Xiaomi/Huawei/Samsung killers): plugin methods `batteryStatus()` / `openBatterySettings()` and a one-time toast with an "Mở cài đặt" button when the app is restricted (native-media.ts `batteryHint`).
- Mobile web / Piper: while a Piper clip plays or loads in a hidden tab, a silent looping `<audio>` stands in between clips so Chrome does not freeze the page during synthesis (`mediasession.ts`, `needsHiddenKeepAlive`).

Not changed on purpose: no audio-focus request in the service. The WebView (Piper) and the TTS engine (native) each request focus themselves, and a third client in the same app would receive AUDIOFOCUS_LOSS from them and pause playback by mistake. Verify call/duck behaviour on a device (step 6).

### Device test steps (needs a real Android 13+ phone, ideally also a Xiaomi/Samsung)
1. Install the APK, open a story, tap listen, accept the notification permission. Expect the notification with Prev/Pause/Next.
2. Native voice: press the power button. Speech must continue without a gap between sentences for 10 minutes and across a chapter change (auto-next on). Lock-screen card shows the chapter title; Pause/Next work from it.
3. Piper voice (Settings > engine): repeat step 2. Also press Home and open another app for 10 minutes.
4. Unplug wired headphones / switch off Bluetooth earbuds while playing: playback pauses.
5. Settings > Battery: set the app to "Restricted", start listening: the toast with "Mở cài đặt" appears once; after "Unrestricted" repeat step 2 for 30 minutes.
6. Incoming call during playback: native and Piper both stop/pause; after the call tap play and it resumes at the same sentence. Open YouTube while playing: playback pauses (focus) and does not talk over it.
7. Swipe the app away from recents: notification disappears and speech stops.
8. Mobile web (Chrome Android, installed PWA or tab): start listening with Piper, lock the screen: audio continues and the media notification controls work.
