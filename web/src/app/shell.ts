/**
 * Behaviour of the static shell (src/components/*.astro): side navigation and its source list, the mobile
 * drawer, the global search box, breadcrumbs, the skip link and the settings buttons.
 */
import type { Route, SettingsTab, Source } from './core/contracts';
import { data, isAbort } from './core/data';
import { debounce, on } from './core/events';
import { fmtNum, matchTokens, normKey, repoLabel, tokens } from './core/format';
import { $, $$, html, render, type SafeHtml } from './core/html';
import { icon } from './core/icons';
import { currentRoute, href, navigate } from './core/router';
import { auth } from './core/auth';
import { announce, closeAllDialogs, toast, trapFocus } from './core/ui';

// ---------------------------------------------------------------- breadcrumbs

export interface Crumb {
  label: string;
  /** Hash of the ancestor; omit for the current page. */
  href?: string;
}

/**
 * Sets the breadcrumb trail of the current view (ancestors first, the current page last and without `href`).
 * The home link is added automatically. An empty list hides the bar. On phones the bar shows a back link to the
 * nearest ancestor next to the current page.
 */
export function setCrumbs(items: Crumb[]): void {
  const el = $('#crumb');
  if (!el) return;
  if (!items.length) {
    el.hidden = true;
    el.replaceChildren();
    return;
  }
  const trail: Crumb[] = [{ label: 'Trang chủ', href: href.home() }, ...items];
  const parent = [...trail].reverse().find((c) => c.href) as Crumb;
  const lis: SafeHtml[] = trail.map((c, i) => {
    const last = i === trail.length - 1;
    const sep = i ? html`<span class="crumb-sep" aria-hidden="true">${icon('right')}</span>` : '';
    return c.href && !last
      ? html`<li class="crumb-item">${sep}<a class="crumb-link" href="${c.href}">${c.label}</a></li>`
      : html`<li class="crumb-item crumb-current">${sep}<span aria-current="page">${c.label}</span></li>`;
  });
  render(
    el,
    html`<a class="crumb-back" href="${parent.href as string}" aria-label="Quay lại ${parent.label}">${icon('left')}</a>
      <ol class="crumb-list">
        ${lis}
      </ol>`,
  );
  el.hidden = false;
}

// ---------------------------------------------------------------- settings panel

/** Opens the settings panel (loaded on demand). */
export function openSettings(tab?: SettingsTab): void {
  void import('./settings/panel').then(
    (m) => m.settingsPanel.open(tab),
    () => toast({ message: 'Không mở được phần Cài đặt. Vui lòng thử lại.', kind: 'error' }),
  );
}

// ---------------------------------------------------------------- side navigation

let sourcesCtl: AbortController | null = null;
let navSources: Source[] = [];
const REPO_CAP = 80;

function repoItems(s: Source, filter: string): SafeHtml {
  const toks = tokens(filter);
  const route = currentRoute();
  const all = s.repos || [];
  const list = toks.length ? all.filter((r) => matchTokens(normKey(repoLabel(r.repo) + ' ' + r.repo), toks)) : all;
  if (!list.length) return html`<li class="nav-empty">Không có kho nào khớp.</li>`;
  const shown = list.slice(0, REPO_CAP);
  return html`${shown.map((r) => {
    const cur = route.view === 'lib' && route.source === s.id && route.repo === r.repo;
    return html`<li><a class="nav-sub" href="${href.lib(s.id, r.repo)}" ${cur ? html`aria-current="page"` : ''}><span class="nav-text">${repoLabel(r.repo)}</span></a></li>`;
  })}${list.length > shown.length ? html`<li class="nav-empty">Còn ${fmtNum(list.length - shown.length)} kho khác, hãy gõ để lọc.</li>` : ''}`;
}

function renderSources(): void {
  const host = $('#nav-sources');
  if (!host) return;
  const route = currentRoute();
  if (!navSources.length) {
    render(host, html`<p class="nav-empty">Chưa có nguồn truyện.</p>`);
    return;
  }
  render(
    host,
    html`<ul class="nav-list">
      ${navSources.map((s) => {
        const cur = route.view === 'lib' && route.source === s.id && !route.repo;
        const repos = s.repos?.length || 0;
        const row = s.available
          ? html`<a class="nav-link nav-source" href="${href.lib(s.id)}" title="${s.name}" ${cur ? html`aria-current="page"` : ''}>
              <span class="dot dot-on" aria-hidden="true"></span><span class="nav-text">${s.name}</span>
            </a>`
          : html`<span class="nav-link nav-source is-off" title="${s.name}">
              <span class="dot" aria-hidden="true"></span><span class="nav-text">${s.name}</span><span class="badge">tạm ngắt</span>
            </span>`;
        const sub =
          s.available && repos
            ? html`<details class="nav-repos" data-source="${s.id}">
                <summary class="nav-repos-sum">${icon('right', 'nav-caret')}<span>${fmtNum(repos)} kho truyện</span></summary>
                <div class="nav-repos-body"></div>
              </details>`
            : '';
        return html`<li>${row}${sub}</li>`;
      })}
    </ul>`,
  );
  for (const d of $$<HTMLDetailsElement>('details.nav-repos', host)) {
    d.addEventListener('toggle', () => {
      const body = d.querySelector<HTMLElement>('.nav-repos-body');
      const s = navSources.find((x) => x.id === d.dataset.source);
      if (!body || !s || !d.open || body.childElementCount) return;
      const id = `nav-filter-${s.id.replace(/[^\w-]/g, '')}`;
      render(
        body,
        html`<label class="sr-only" for="${id}">Lọc kho truyện</label>
          <input id="${id}" class="input input-sm nav-filter" type="search" placeholder="Lọc kho…" autocomplete="off" spellcheck="false" />
          <ul class="nav-list nav-sublist">
            ${repoItems(s, '')}
          </ul>`,
      );
      const input = body.querySelector<HTMLInputElement>('input') as HTMLInputElement;
      const ul = body.querySelector<HTMLElement>('ul') as HTMLElement;
      input.addEventListener('input', () => render(ul, repoItems(s, input.value)));
    });
    // keep the list of the source being browsed open
    if (route.view === 'lib' && route.source === d.dataset.source && route.repo && route.repo !== '*') d.open = true;
  }
}

/** Loads the source list into the side navigation (again after the data source changed). */
export async function refreshSources(): Promise<void> {
  sourcesCtl?.abort();
  const ctl = (sourcesCtl = new AbortController());
  try {
    const j = await data.sources({ signal: ctl.signal });
    navSources = j.sources || [];
  } catch (e) {
    if (isAbort(e)) return;
    navSources = [];
  }
  if (!ctl.signal.aborted) renderSources();
}

function markCurrent(route: Route): void {
  for (const a of $$<HTMLAnchorElement>('#sidenav [data-nav]')) {
    if (a.dataset.nav === route.view) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  }
  for (const a of $$<HTMLAnchorElement>('#nav-sources a')) {
    if (a.getAttribute('href') === route.path) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  }
  for (const [id, view] of [
    ['btn-history', 'history'],
    ['btn-bookmarks', 'bookmarks'],
  ] as const) {
    const a = document.getElementById(id);
    if (!a) continue;
    if (route.view === view) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  }
}

// ---------------------------------------------------------------- mobile drawer

let releaseDrawer: (() => void) | null = null;
const isDrawerMode = (): boolean => matchMedia('(max-width: 1023px)').matches || document.body.classList.contains('view-read');

export function closeDrawer(): void {
  if (!releaseDrawer) return;
  const r = releaseDrawer;
  releaseDrawer = null;
  document.documentElement.classList.remove('nav-open');
  $('#menu-btn')?.setAttribute('aria-expanded', 'false');
  const scrim = $('#sidenav-scrim');
  if (scrim) scrim.hidden = true;
  const nav = $('#sidenav');
  nav?.removeAttribute('role');
  nav?.removeAttribute('aria-modal');
  r();
}

export function openDrawer(): void {
  const nav = $('#sidenav');
  if (!nav || releaseDrawer || !isDrawerMode()) return;
  document.documentElement.classList.add('nav-open');
  $('#menu-btn')?.setAttribute('aria-expanded', 'true');
  const scrim = $('#sidenav-scrim');
  if (scrim) scrim.hidden = false;
  nav.setAttribute('role', 'dialog');
  nav.setAttribute('aria-modal', 'true');
  releaseDrawer = trapFocus(nav, closeDrawer);
  $('#sidenav-close')?.focus({ preventScroll: true });
}

// ---------------------------------------------------------------- search box

function bindSearch(): void {
  const form = $<HTMLFormElement>('#search-form');
  const input = $<HTMLInputElement>('#q');
  const clear = $<HTMLButtonElement>('#search-clear');
  const toggle = $<HTMLButtonElement>('#search-toggle');
  const close = $<HTMLButtonElement>('#search-close');
  const bar = $('#topbar');
  if (!form || !input || !bar) return;

  const syncClear = (): void => {
    if (clear) clear.hidden = !input.value;
  };
  const go = (replace: boolean): void => {
    const q = input.value.trim();
    const onSearch = currentRoute().view === 'search';
    if (!q && !onSearch) return;
    navigate(href.search(q), { replace: replace && onSearch });
  };
  const typed = debounce(() => go(true), 200);

  input.addEventListener('input', () => {
    syncClear();
    typed();
  });
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    typed.cancel();
    go(true);
    input.blur();
  });
  clear?.addEventListener('click', () => {
    input.value = '';
    syncClear();
    typed.cancel();
    if (currentRoute().view === 'search') navigate(href.search(''), { replace: true });
    input.focus();
  });

  const setOpen = (open: boolean): void => {
    bar.classList.toggle('search-open', open);
    toggle?.setAttribute('aria-expanded', String(open));
    if (open) input.focus();
  };
  toggle?.addEventListener('click', () => setOpen(true));
  close?.addEventListener('click', () => {
    setOpen(false);
    toggle?.focus();
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && bar.classList.contains('search-open')) {
      setOpen(false);
      toggle?.focus();
    }
  });
  // "/" focuses the search box, like most reading sites
  document.addEventListener('keydown', (e) => {
    if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey) return;
    const t = e.target as HTMLElement | null;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (document.documentElement.classList.contains('has-overlay') || document.body.classList.contains('view-read')) return;
    e.preventDefault();
    if (toggle && getComputedStyle(toggle).display !== 'none') setOpen(true);
    else input.focus();
  });

  on('route', (r) => {
    if (r.view === 'search') {
      const q = r.query.q || '';
      if (document.activeElement !== input && input.value !== q) input.value = q;
    } else {
      input.value = '';
      bar.classList.remove('search-open');
      toggle?.setAttribute('aria-expanded', 'false');
    }
    syncClear();
  });
}

// ---------------------------------------------------------------- route change focus

/**
 * After a route change keep keyboard / screen-reader users oriented (WCAG 2.4.3, 4.1.3): focus the main landmark
 * (without scrolling) and announce the page title once the view has had a moment to set it. The reader manages its
 * own focus, and a user who is typing in a field (e.g. the search box) keeps it.
 */
export function moveFocusToView(view: string): void {
  if (view === 'read') return;
  setTimeout(() => {
    const a = document.activeElement;
    if (a && /^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)) return;
    if (a && a.closest('[role="dialog"]')) return;
    $('#view')?.focus({ preventScroll: true });
    announce(document.title);
  }, 150);
}

// ---------------------------------------------------------------- init

let started = false;
/** Wires the shell. Called once by main.ts. */
export function init(): void {
  if (started) return;
  started = true;

  // the skip link must not change the hash (the hash is the route)
  $('#skip-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    const main = $('#view');
    main?.focus({ preventScroll: true });
    main?.scrollIntoView({ block: 'start' });
  });

  $('#menu-btn')?.addEventListener('click', () => (releaseDrawer ? closeDrawer() : openDrawer()));
  $('#sidenav-close')?.addEventListener('click', closeDrawer);
  $('#sidenav-scrim')?.addEventListener('click', closeDrawer);
  $('#sidenav')?.addEventListener('click', (e) => {
    if ((e.target as Element).closest('a[href]')) closeDrawer();
  });
  matchMedia('(min-width: 1024px)').addEventListener('change', closeDrawer);

  for (const id of ['btn-settings', 'nav-settings']) {
    document.getElementById(id)?.addEventListener('click', () => {
      closeDrawer();
      openSettings();
    });
  }

  // the account entries exist only when the server offers Google sign-in
  const paintAccount = (): void => {
    const on = auth.available() || auth.signedIn();
    for (const id of ['btn-account', 'nav-account']) {
      const b = document.getElementById(id);
      if (!b) continue;
      b.hidden = !on;
      b.setAttribute('aria-label', auth.signedIn() ? `Tài khoản: ${auth.user()?.name || auth.user()?.email || 'Google'}` : 'Đăng nhập bằng Google');
      b.classList.toggle('is-signed-in', auth.signedIn());
      const label = b.querySelector('span');
      if (label) label.textContent = auth.signedIn() ? 'Tài khoản' : 'Đăng nhập';
      b.title = auth.signedIn() ? 'Tài khoản' : 'Đăng nhập bằng Google';
    }
  };
  for (const id of ['btn-account', 'nav-account']) {
    document.getElementById(id)?.addEventListener('click', () => {
      closeDrawer();
      openSettings('account');
    });
  }
  paintAccount();
  auth.onChange(paintAccount);

  bindSearch();

  let firstRoute = true;
  on('route', (r) => {
    closeDrawer();
    closeAllDialogs();
    markCurrent(r);
    if (!firstRoute) moveFocusToView(r.view);
    firstRoute = false;
    // crumbs belong to the view that set them: a view without crumbs gets none
    if (r.view === 'home' || r.view === 'read') setCrumbs([]);
    for (const d of $$<HTMLDetailsElement>('details.nav-repos')) {
      if (r.view === 'lib' && r.source === d.dataset.source && r.repo && r.repo !== '*') d.open = true;
    }
  });
  on('backend', () => void refreshSources());
}

export const shell = { init, setCrumbs, openSettings, refreshSources, openDrawer, closeDrawer };
