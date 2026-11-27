# MythLab extension (Chrome, Edge, Brave, Opera)

Manifest V3, no build step. Click the toolbar icon (or Alt+M) and MythLab opens in the side panel,
so the story keeps playing on any tab. Voices run on the device (Piper WASM), as on the web.

Install for development: `chrome://extensions` → Developer mode → Load unpacked → this folder.
Package: `node pack.mjs` writes `dist/MythLab-extension-<version>.zip` (also served from
https://myth.xlabrnd.com/extension/). Chrome Web Store upload is manual (needs a developer account).
