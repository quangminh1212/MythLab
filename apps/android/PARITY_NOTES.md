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
