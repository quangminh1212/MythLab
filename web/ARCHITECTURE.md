# MythLab web: architecture

Static single-page app built with Astro (one page, `build.format: 'file'`, `assetsPrefix: '.'`), TypeScript strict,
hash routing. The output in `dist/` works from any path and from `file://`-like hosts: every reference is relative
(`./_astro/...`, `./boot.js`, `./fonts/fonts.css`, `./icons/*`). There are no inline scripts and no inline styles.

## Commands

| Command | What it does |
| --- | --- |
| `npm run dev` | Astro dev server on 4321 |
| `npm run build` | static build into `dist/` |
| `npm run check` | `astro check` (types for `.astro` and `.ts`) |
| `npm test` | vitest (happy-dom + fake-indexeddb, `src/test-setup.ts`) |
| `cd e2e && go test -count=1 -timeout 40m ./...` | Go (chromedp) end-to-end suites against the built `dist/`: browse views (2 viewports x 3 themes; console/HTTP errors, overflow, DOM size, tap targets, contrast), reader, settings, offline |

## Module map

```
src/pages/index.astro        the only page; static shell + home skeleton
src/layouts/Base.astro       <head>, boot.js, fonts, the entry <script> (imports app/main.ts)
src/components/*.astro       TopBar, SideNav, Brand, Icon, HomeSkeleton, Overlays (static markup only)
src/styles/                  tokens.css -> base.css -> shell.css -> components.css -> views.css
                             reader.css, player.css, settings.css (owned by the reader/player/settings stages)
public/boot.js               pre-paint theme + boot-error fallback (classic script, no module)
public/fonts, public/icons   self-hosted woff2 + fonts.css, app icons

src/app/main.ts              boot: migrate storage, settings, backend, shell, router, lazy view table
src/app/shell.ts             top bar, side nav / drawer, breadcrumbs, global search box, source list
src/app/core/
  contracts.ts               shared types: Route, ViewModule, ViewContext, Progress, Bookmark, Follow,
                             PlayerApi, SettingsPanelApi, OfflineApi, PwaApi, AppEvents
  html.ts                    html`` / raw / join / render / esc (see "html helper rule")
  router.ts                  parseHash, href builders, navigate, setQuery, start
  store.ts                   localStorage JSON store (mythlab.* keys), IndexedDB "mythlab" v1, legacy migration
  settings.ts                settings model, clamp/normalise, apply to <html> (data-theme, --read-* variables)
  progress.ts                reading positions (mythlab.progress), debounced writes, cross-tab merge
  library.ts                 history, bookmarks, follows
  backend/                   index.ts picks server or GitHub-direct; server.ts, github.ts, types.ts
  data.ts                    cached reads on top of backend: sources, stories, story, chapter, search
  textutil.ts                chapter name parsing, text cleaning (same cases as the Go server testdata)
  format.ts, events.ts       pure helpers; typed event bus
  ui.ts                      toast, dialogs + focus trap, virtualList, stateView/showError, skeleton, announce
  covers.ts, fonts.ts, icons.ts
src/app/views/               one module per route: home, library, search, story, history, bookmarks,
                             onboarding, reader; cards.ts holds the shared card/tile/head templates
src/app/player/index.ts      exports `player: PlayerApi`
src/app/settings/panel.ts    exports `settingsPanel: SettingsPanelApi`
src/app/offline/index.ts     exports `offline: OfflineApi`
src/app/pwa.ts               exports `pwa: PwaApi`
```

Routes: `#/`, `#/lib/<source>`, `#/lib/<source>/<repo>`, `#/lib/<source>/*`, `#/s/<source>/<key>`,
`#/r/<source>/<key>/<idx>?p=<para>`, `#/search?q=`, `#/history`, `#/bookmarks`.

## Conventions

- Views are loaded lazily by `main.ts`; `core/` never imports from `views/`, `player/`, `settings/` or `offline/`.
- All network reads go through `core/data.ts` (or `backend` for URLs); views never call `fetch` directly.
- All persistence goes through `core/store.ts`, `core/settings.ts`, `core/progress.ts`, `core/library.ts`. The storage
  key names and shapes are frozen (shared with the old reader and the native apps).
- Every async view passes `ctx.signal` down and ignores `isAbort` errors; `unmount()` removes listeners and timers.
- Long lists (chapters) use `ui.virtualList`; a page must stay under roughly 2,000 DOM nodes.
- Loading, empty and error states use `ui.skeleton`, `ui.stateView`, `ui.showError(el, e, retry)`.
- Each view renders exactly one `<h1>` and calls `ctx.setTitle`.
- User-facing text is Vietnamese; code and comments are English.
- No inline `style=""`: dynamic values go through CSS custom properties with `cssVars()` or classes.
- Interactive targets are at least `var(--tap)` (44 px) on coarse pointers and under 720 px.
- Single-column grids use `grid-template-columns: minmax(0, 1fr)` so long titles cannot widen the page.

## html helper rule

Never assign strings to `innerHTML`. Build markup with the tagged template and hand it to `render`:

```ts
import { html, join, raw, render } from '../core/html';
render(el, html`<ul>${join(items.map((s) => html`<li><a href="${href.story(src, s.key)}">${s.name}</a></li>`))}</ul>`);
```

Every interpolated value is escaped unless it is a `SafeHtml` (the result of `html`, `join`, `icon()`, `cover()`),
`null`/`undefined`/`false` (rendered as nothing) or an array of those. `raw()` is only for markup the app itself
produced (for example a generated SVG); never pass server or user text to it.

## How to add a view

1. Create `src/app/views/<name>.ts` exporting `mount(el, route, ctx)` and, if needed, `unmount()` / `update(route)`
   (the `ViewModule` contract in `core/contracts.ts`).
2. Add the route to `parseHash` and an `href.<name>()` builder in `core/router.ts`, and the view name to `ViewName` in `core/contracts.ts`.
3. Register the lazy import in the view table in `src/app/main.ts`.
4. Put styles in `src/styles/views.css` (or the stage's own stylesheet) using the tokens below.
5. Add a case to `e2e/browse_test.go` and unit tests for any pure helper.

## CSS tokens (`src/styles/tokens.css`)

Themes are selected by `html[data-scheme="light|dark|sepia"]`; use tokens, never literal colours.

- Colour: `--bg --surface --surface-2 --surface-3 --text --text-2 --muted --border --border-strong --brand --accent
  --accent-hover --accent-ink --accent-text --danger --danger-bg --ok --hl --scrim --header-bg --skeleton
  --skeleton-hi --toast-bg --toast-fg --cover-l`
- Type: `--font-ui --font-display --font-read --fs-xs --fs-sm --fs-md --fs-lg --fs-xl --fs-2xl`
- Shape and motion: `--radius-sm --radius --radius-lg --radius-pill --shadow-sm --shadow --shadow-lg --dur --ease`
- Layout: `--page-max --page-gap --gutter --side-w --topbar-h --player-h --tap`
- Reader (set by `settings.apply`): `--read-bg --read-fg --read-accent --read-size --read-line --read-width
  --read-gap --read-indent --read-align --read-weight --read-letter --read-word --brightness`
- Layers: `--z-raised --z-topbar --z-sidenav --z-player --z-scrim --z-drawer --z-overlay --z-dim --z-toast`

## Build note: relative preloads

Vite writes dynamic-import preload lists as `./_astro/x.js`, which the browser resolves against the importing chunk
(already inside `_astro/`). The `relativePreload` integration in `astro.config.mjs` rewrites those entries to `./x.js`
after the build. Anything that post-processes or precaches `dist/_astro/*.js` must run after `astro build` finishes.
