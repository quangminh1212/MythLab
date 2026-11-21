/**
 * Reader view: one chapter in a centred column, in scroll mode or in pages (CSS columns).
 *
 * Route `#/r/<source>/<key>/<idx>` (idx 0-based). Query: `?p=<paragraph>` opens the chapter at that paragraph
 * (bookmarks), `?end=1` opens it at its last page (turning back from the next chapter). Both are removed from the
 * address once applied, so a reload restores the saved position instead of repeating them.
 *
 * The position is { para, frac } at a reading line (scroll mode) or the first paragraph of the page (page mode);
 * it is saved on a short debounce, on page hide and on unmount, and restored again once the fonts have loaded.
 * The sentence the player is speaking is followed through `player/mark` without loading the player.
 */
import type { Chapter, ChapterRef, Route, StoryDetail, ViewContext } from '../core/contracts';
import { data, isAbort } from '../core/data';
import { debounce, on } from '../core/events';
import { chapterLabel, fmtNum } from '../core/format';
import { html, render, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { library } from '../core/library';
import { progress } from '../core/progress';
import { href, navigate, setQuery } from '../core/router';
import { S, settings } from '../core/settings';
import { openDialog, showError, skeleton, toast, announce, type DialogHandle } from '../core/ui';
import { createAutoScroll, SPEEDS, type AutoScroll } from '../reader/autoscroll';
import { closeChapterDrawer, openChapterDrawer, type DrawerTab } from '../reader/drawer';
import { createHighlighter } from '../reader/highlight';
import { openHelp } from '../reader/help';
import { xicon } from '../reader/icons';
import { keyOf, shortcutAllowed, typingTarget } from '../reader/keys';
import { chapterSwipe, clampPage, firstPara, pageCount, pageOfOffset, pageSwipe, tapZone, turn, wheelTurn, stride, type PageGeom } from '../reader/pager';
import { anchorAt, excerpt, scrollFor, scrollFraction, startPosition, type Anchor } from '../reader/position';
import { currentMark, onMark, type SpeechMark } from '../player/mark';
import { openSettings, shell } from '../shell';

/** Distance of the reading line from the top of the viewport (scroll mode), in px. */
/** Keys that act alone (no modifier) and can be switched off in Settings. */
const SINGLE_KEYS: ReadonlySet<string> = new Set(['m', 'b', 'a', '+', '=', '-', '_', '?', ' ']);
const LINE = 84;
/** Gap between two pages, in px. */
const GAP = 48;
const HIDE_AFTER = 4000;

let teardown: (() => void) | null = null;
let live: { goto(route: Route): void } | null = null;

const selecting = (): boolean => {
  const s = window.getSelection();
  return !!s && !s.isCollapsed && s.toString().trim() !== '';
};
const overlayOpen = (): boolean => document.documentElement.classList.contains('has-overlay');

interface Ctx {
  el: HTMLElement;
  ctx: ViewContext;
  st: StoryDetail;
  idx: number;
  ref: ChapterRef;
  ch: Chapter;
  label: string;
  route: Route;
}

function btn(act: string, label: string, content: SafeHtml, cls = ''): SafeHtml {
  return html`<button type="button" class="icon-btn ${cls}" data-act="${act}" aria-label="${label}" title="${label}">${content}</button>`;
}

function markup(c: Ctx): SafeHtml {
  const { st, idx, label, ch } = c;
  const total = st.chapters.length;
  const storyHref = href.story(st.source, st.key);
  const prev = idx > 0 ? href.read(st.source, st.key, idx - 1) : '';
  const next = idx < total - 1 ? href.read(st.source, st.key, idx + 1) : '';
  return html`<div class="rd" id="rd" data-mode="${S.readMode}">
    <div class="rd-bar" aria-hidden="true"><div class="rd-bar-fill" id="rd-fill"></div></div>
    <header class="rd-chrome" id="rd-chrome">
      <a class="icon-btn" href="${storyHref}" aria-label="Về trang truyện" title="Về trang truyện">${icon('left')}</a>
      <div class="rd-ct">
        <span class="rd-ct-story">${st.name}</span>
        <span class="rd-ct-pos" id="rd-ct-pos"></span>
      </div>
      ${btn('prev', 'Chương trước', xicon('chapterPrev'))}
      ${btn('next', 'Chương sau', xicon('chapterNext'))}
      ${btn('toc', 'Mục lục chương (M)', icon('list'))}
      <button type="button" class="icon-btn rd-wide" data-act="mark" aria-label="Đánh dấu đoạn này (B)" title="Đánh dấu đoạn này (B)" aria-pressed="false">${icon('bookmark')}</button>
      <button type="button" class="icon-btn rd-wide rd-auto-btn" data-act="auto" aria-label="Tự cuộn (A)" title="Tự cuộn (A)" aria-pressed="false">${xicon('autoScroll')}</button>
      <button type="button" class="icon-btn" data-act="listen" aria-label="Nghe đọc (Phím cách)" title="Nghe đọc (Phím cách)" aria-pressed="false">${icon('headphones')}</button>
      ${btn('settings', 'Cài đặt', icon('settings'), 'rd-wide')}
      ${btn('help', 'Phím tắt (?)', xicon('help'), 'rd-wide')}
      ${btn('more', 'Thêm', xicon('more'), 'rd-narrow')}
    </header>
    <div class="rd-stage" id="rd-stage">
      <div class="rd-clip" id="rd-clip">
        <article class="rd-article" id="rd-cols">
          <header class="rd-head">
            <p class="rd-story"><a class="rd-story-link" href="${storyHref}">${st.name}</a></p>
            <h1 class="rd-title" id="rd-title">${label}</h1>
          </header>
          <div class="rd-body" id="rd-body">${ch.paragraphs.map((p, i) => html`<p data-i="${i}">${p}</p>`)}</div>
          <nav class="rd-end" aria-label="Chuyển chương">
            ${next
              ? html`<p class="rd-end-note">Hết chương ${st.chapters[idx]?.n ?? idx + 1}</p>`
              : html`<p class="rd-end-note">Bạn đã đọc đến chương cuối của truyện này.</p>`}
            <div class="rd-end-row">
              ${prev ? html`<a class="btn" href="${prev}" data-end-nav="prev" rel="prev">${icon('left')}<span>Chương trước</span></a>` : html`<span></span>`}
              <a class="btn" href="${storyHref}">${icon('list')}<span>Mục lục</span></a>
              ${next ? html`<a class="btn btn-primary" href="${next}" data-end-nav="next" rel="next"><span>Chương sau</span>${icon('right')}</a>` : html`<span></span>`}
            </div>
          </nav>
        </article>
      </div>
    </div>
    <div class="rd-pager-pos" id="rd-pager-pos" aria-hidden="true"></div>
    <div class="rd-auto" id="rd-auto" role="group" aria-label="Tự cuộn" hidden>
      <button type="button" class="icon-btn" data-act="auto-slower" aria-label="Chậm hơn (−)">${xicon('minus')}</button>
      <span class="rd-auto-level" id="rd-auto-level" aria-live="polite"></span>
      <button type="button" class="icon-btn" data-act="auto-faster" aria-label="Nhanh hơn (+)">${xicon('plus')}</button>
      <button type="button" class="btn btn-sm" data-act="auto-stop">Dừng</button>
    </div>
  </div>`;
}

function open(c: Ctx): void {
  const { el, ctx, st, idx, ref, ch, label } = c;
  const total = st.chapters.length;
  const paragraphs = ch.paragraphs;
  render(el, markup(c));

  const root = el.querySelector<HTMLElement>('#rd') as HTMLElement;
  const chrome = el.querySelector<HTMLElement>('#rd-chrome') as HTMLElement;
  const stage = el.querySelector<HTMLElement>('#rd-stage') as HTMLElement;
  const clip = el.querySelector<HTMLElement>('#rd-clip') as HTMLElement;
  const cols = el.querySelector<HTMLElement>('#rd-cols') as HTMLElement;
  const titleEl = el.querySelector<HTMLElement>('#rd-title');
  const fill = el.querySelector<HTMLElement>('#rd-fill') as HTMLElement;
  const posEl = el.querySelector<HTMLElement>('#rd-ct-pos') as HTMLElement;
  const pagerPos = el.querySelector<HTMLElement>('#rd-pager-pos') as HTMLElement;
  const autoBar = el.querySelector<HTMLElement>('#rd-auto') as HTMLElement;
  const autoLevel = el.querySelector<HTMLElement>('#rd-auto-level') as HTMLElement;
  const paras = Array.from(el.querySelectorAll<HTMLElement>('#rd-body > p'));
  const ac = new AbortController();
  const sig = { signal: ac.signal };
  const subs: (() => void)[] = [];
  const timers = new Set<ReturnType<typeof setTimeout>>();
  const later = (fn: () => void, ms: number): ReturnType<typeof setTimeout> => {
    const t = setTimeout(() => {
      timers.delete(t);
      fn();
    }, ms);
    timers.add(t);
    return t;
  };

  const hl = createHighlighter({ paraEl: (i) => paras[i] ?? null, paraText: (i) => paragraphs[i] ?? '', titleEl });
  const paged = (): boolean => S.readMode === 'page';

  // ------------------------------------------------------------ state
  let ready = false;
  let userAt = 0;
  let ignoreScrollUntil = 0;
  let lastAnchor: Anchor = { para: 0, frac: 0 };
  let lastY = 0;
  let frac = 0;
  let page = 0;
  let pages = 1;
  let starts: number[] = [];
  let ends: number[] = [];
  let geom: PageGeom = { width: 0, gap: GAP, scrollWidth: 0 };
  let lastWheel = 0;
  let tapTimer: ReturnType<typeof setTimeout> | undefined;
  let chromeTimer: ReturnType<typeof setTimeout> | undefined;
  let playing = false;

  // ------------------------------------------------------------ position
  const boxOf = (i: number): { top: number; height: number } => {
    const r = (paras[i] as HTMLElement).getBoundingClientRect();
    return { top: r.top, height: r.height };
  };

  function scrollAnchor(): Anchor {
    return anchorAt(paras.length, boxOf, LINE);
  }

  function pageAnchor(): Anchor {
    const para = firstPara(starts, ends, page);
    const s = starts[para] ?? page;
    const e = ends[para] ?? page;
    return { para, frac: s < page ? Math.round(((page - s) / (e - s + 1)) * 10000) / 10000 : 0 };
  }

  const currentAnchor = (): Anchor => (paras.length ? (paged() ? pageAnchor() : scrollAnchor()) : { para: 0, frac: 0 });

  function pageFor(a: Anchor): number {
    const s = starts[a.para];
    const e = ends[a.para];
    if (s == null || e == null) return 0;
    return clampPage(s + Math.floor(a.frac * (e - s + 1) + 1e-6), pages);
  }

  function toScroll(y: number): void {
    ignoreScrollUntil = performance.now() + 200;
    window.scrollTo(0, y);
  }

  function restoreScroll(a: Anchor, mode: 'line' | 'top' | 'end'): void {
    const root2 = document.scrollingElement || document.documentElement;
    const max = Math.max(0, root2.scrollHeight - window.innerHeight);
    if (mode === 'end') return toScroll(max);
    if (mode === 'top' || !paras[a.para]) return toScroll(0);
    const r = (paras[a.para] as HTMLElement).getBoundingClientRect();
    toScroll(scrollFor({ top: r.top + window.scrollY, height: r.height }, a.frac, LINE, max));
  }

  const savePos = (now = false, skipSame = false): void => {
    if (!ready) return;
    const a = currentAnchor();
    lastAnchor = a;
    progress.saveReading(st, idx, a.para, a.frac, { now, skipSame });
  };
  const saveSoon = debounce(() => savePos(), 300);

  // ------------------------------------------------------------ chrome
  function updateUi(): void {
    const f = paged() ? (pages > 1 ? page / (pages - 1) : 1) : frac;
    fill.style.setProperty('--p', String(Math.round(f * 1000) / 1000));
    posEl.textContent = `Chương ${idx + 1}/${fmtNum(total)} · ${Math.round(f * 100)}%`;
    pagerPos.textContent = paged() ? `Trang ${page + 1}/${pages}` : '';
    (chrome.querySelector('[data-act="prev"]') as HTMLButtonElement).disabled = idx <= 0;
    (chrome.querySelector('[data-act="next"]') as HTMLButtonElement).disabled = idx >= total - 1;
  }

  function showChrome(): void {
    root.classList.remove('rd-hide');
    scheduleHide();
  }
  function scheduleHide(): void {
    if (chromeTimer) clearTimeout(chromeTimer);
    chromeTimer = later(() => {
      if (chrome.matches(':hover') || chrome.querySelector(':focus-visible') || overlayOpen()) return scheduleHide();
      root.classList.add('rd-hide');
    }, HIDE_AFTER);
  }
  function hideChrome(): void {
    if (chromeTimer) clearTimeout(chromeTimer);
    if (chrome.querySelector(':focus-visible')) return;
    root.classList.add('rd-hide');
  }
  const toggleChrome = (): void => (root.classList.contains('rd-hide') ? showChrome() : hideChrome());

  // ------------------------------------------------------------ pages
  function layoutPages(): void {
    const w = Math.floor(clip.clientWidth);
    const h = Math.floor(clip.clientHeight);
    root.style.setProperty('--pw', String(w));
    root.style.setProperty('--ph', String(h));
    root.style.setProperty('--pg', String(GAP));
    geom = { width: w, gap: GAP, scrollWidth: cols.scrollWidth };
    pages = pageCount(geom);
    root.style.setProperty('--stride', String(stride(geom)));
    const base = cols.getBoundingClientRect().left;
    starts = [];
    ends = [];
    for (const p of paras) {
      const rs = p.getClientRects();
      const first = rs[0];
      const last = rs[rs.length - 1];
      if (!first || !last) {
        starts.push(starts[starts.length - 1] ?? 0);
        ends.push(ends[ends.length - 1] ?? 0);
        continue;
      }
      starts.push(pageOfOffset(first.left - base + 1, geom, pages));
      ends.push(pageOfOffset(last.right - base - 1, geom, pages));
    }
  }

  function setPage(p: number): void {
    page = clampPage(p, pages);
    root.style.setProperty('--page', String(page));
    updateUi();
    saveSoon();
  }

  function pageOfEl(target: HTMLElement): number {
    const r = target.getClientRects()[0];
    if (!r) return page;
    return pageOfOffset(r.left - cols.getBoundingClientRect().left + 1, geom, pages);
  }

  // ------------------------------------------------------------ applying the layout
  let applied = '';
  function applyMode(): void {
    const m = S.readMode;
    root.dataset.mode = m;
    if (m === 'page') {
      auto.stop();
      window.scrollTo(0, 0);
    }
    applied = m;
  }

  function relayout(a: Anchor = lastAnchor): void {
    if (applied !== S.readMode) applyMode();
    if (paged()) {
      layoutPages();
      setPage(pageFor(a));
    } else {
      root.style.setProperty('--page', '0');
      restoreScroll(a, a.para === 0 && a.frac === 0 ? 'top' : 'line');
      onScroll();
    }
    lastAnchor = a;
  }

  // ------------------------------------------------------------ navigation
  function go(to: number, atEnd = false): void {
    if (to < 0 || to >= total) return;
    savePos(true);
    navigate(href.read(st.source, st.key, to, atEnd ? { end: 1 } : undefined), { replace: true });
  }

  function turnPages(d: number): void {
    const t = turn(page, d, pages, idx, total);
    if (t.kind === 'page') setPage(t.page);
    else if (t.kind === 'next') go(idx + 1);
    else if (t.kind === 'prev') go(idx - 1, true);
    else if (t.kind === 'end') toast('Đã hết truyện');
  }

  function gotoPara(p: number): void {
    const i = Math.max(0, Math.min(paras.length - 1, Math.trunc(p) || 0));
    if (paged()) setPage(pageFor({ para: i, frac: 0 }));
    else restoreScroll({ para: i, frac: 0 }, 'line');
  }

  // ------------------------------------------------------------ bookmarks
  const here = (): number => currentAnchor().para;
  function markSync(): void {
    const b = chrome.querySelector<HTMLElement>('[data-act="mark"]');
    if (!b) return;
    const on2 = !!library.findBookmark(st.source, st.key, ref.file, here());
    b.setAttribute('aria-pressed', String(on2));
    b.classList.toggle('is-on', on2);
  }
  function toggleMark(): void {
    const para = here();
    const text = paragraphs[para] ?? '';
    const now = library.toggleBookmark({ source: st.source, key: st.key, name: st.name, idx, n: ref.n, file: ref.file, title: label, para, excerpt: excerpt(text) });
    toast(now ? 'Đã đánh dấu đoạn này' : 'Đã bỏ đánh dấu');
    announce(now ? 'Đã đánh dấu đoạn này' : 'Đã bỏ đánh dấu');
    markSync();
  }

  // ------------------------------------------------------------ auto-scroll
  const auto: AutoScroll = createAutoScroll({
    onChange(running, level) {
      autoBar.hidden = !running;
      autoLevel.textContent = `Tốc độ ${level}/${SPEEDS.length}`;
      const b = chrome.querySelector<HTMLElement>('[data-act="auto"]');
      b?.setAttribute('aria-pressed', String(running));
      b?.classList.toggle('is-on', running);
      if (running) hideChrome();
    },
    onEnd() {
      toast('Đã cuộn hết chương');
      showChrome();
    },
    onStep() {
      ignoreScrollUntil = performance.now() + 80;
    },
  });

  function toggleAuto(): void {
    if (paged()) {
      toast('Tự cuộn chỉ dùng ở chế độ cuộn');
      return;
    }
    auto.toggle();
  }

  // ------------------------------------------------------------ listening
  async function listen(para?: number): Promise<void> {
    const { player } = await import('../player/index');
    if (ac.signal.aborted && !player.matches(st.source, st.key)) return;
    if (para == null && player.matches(st.source, st.key, idx)) {
      player.toggle();
      return;
    }
    auto.stop();
    await player.start({ source: st.source, key: st.key, idx, para: para ?? here(), story: st, exact: true });
  }

  function syncListen(status: string): void {
    playing = status === 'playing' || status === 'loading';
    const b = chrome.querySelector<HTMLElement>('[data-act="listen"]');
    b?.setAttribute('aria-pressed', String(playing));
    b?.classList.toggle('is-on', playing);
    if (playing) auto.stop();
  }
  subs.push(on('player', (s) => syncListen(s.status)));
  if (document.getElementById('player-dock')?.childElementCount) void import('../player/index').then(({ player }) => !ac.signal.aborted && syncListen(player.getState().status));

  function followEl(target: HTMLElement, force = false): void {
    if (!force && performance.now() - userAt < 4000) return;
    if (paged()) {
      const p = pageOfEl(target);
      if (p !== page) setPage(p);
      return;
    }
    const r = target.getBoundingClientRect();
    const dock = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--player-h')) || 0;
    if (r.top < LINE || r.bottom > window.innerHeight - dock - 56) toScroll(Math.max(0, window.scrollY + r.top - window.innerHeight * 0.3));
  }

  function applyMark(m: SpeechMark | null): void {
    if (!m || m.source !== st.source || m.key !== st.key || m.idx !== idx) {
      hl.clear();
      return;
    }
    const target = hl.set(m.para, m.s, m.e);
    // while the voice is reading, the sentence change itself brings the text back into view
    if (target && S.follow) followEl(target, playing);
  }
  subs.push(onMark(applyMark));
  applyMark(currentMark());

  // ------------------------------------------------------------ scrolling
  let rafScroll = 0;
  function onScroll(): void {
    if (paged() || !ready) return;
    if (rafScroll) return;
    rafScroll = requestAnimationFrame(() => {
      rafScroll = 0;
      const root2 = document.scrollingElement || document.documentElement;
      frac = scrollFraction(window.scrollY, root2.scrollHeight, window.innerHeight);
      lastAnchor = scrollAnchor();
      updateUi();
      saveSoon();
      markSync();
      const dy = window.scrollY - lastY;
      lastY = window.scrollY;
      if (performance.now() > ignoreScrollUntil) {
        if (dy > 6) hideChrome();
        else if (dy < -6) showChrome();
      }
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true, ...sig });

  const touched = (): void => {
    userAt = performance.now();
    auto.hold(1500);
  };
  for (const t of ['wheel', 'touchstart', 'pointerdown'] as const) window.addEventListener(t, touched, { passive: true, capture: true, ...sig });

  // ------------------------------------------------------------ pointer: tap zones, double click, wheel, swipe
  // a click that only dismisses a selection must not turn the page: the browser clears it before `click` fires
  let selAtDown = false;
  stage.addEventListener('pointerdown', () => (selAtDown = selecting()), { capture: true, ...sig });
  stage.addEventListener(
    'click',
    (e) => {
      if (e.defaultPrevented || e.button) return;
      const t = e.target as Element;
      if (t.closest('a, button, input, select, textarea')) return;
      if (tapTimer) clearTimeout(tapTimer);
      if (e.detail > 1 || selecting() || selAtDown) return;
      const x = e.clientX;
      const touch = (e as PointerEvent).pointerType === 'touch';
      // a short delay lets a double click (listen from here) cancel the tap
      tapTimer = later(() => {
        if (selecting()) return;
        if (paged() && S.tapZones) {
          const z = tapZone(x, window.innerWidth);
          if (z === 'prev') turnPages(-1);
          else if (z === 'next') turnPages(1);
          else toggleChrome();
        } else if (touch || paged()) toggleChrome();
      }, 260);
    },
    sig,
  );

  stage.addEventListener(
    'dblclick',
    (e) => {
      if (tapTimer) clearTimeout(tapTimer);
      const p = (e.target as Element).closest<HTMLElement>('#rd-body > p');
      if (!p) return;
      window.getSelection()?.removeAllRanges();
      void listen(Number(p.dataset.i) || 0);
    },
    sig,
  );

  stage.addEventListener(
    'wheel',
    (e) => {
      if (!paged() || e.ctrlKey) return;
      e.preventDefault();
      const now = performance.now();
      const d = wheelTurn(Math.abs(e.deltaY) >= Math.abs(e.deltaX) ? e.deltaY : e.deltaX, now, lastWheel);
      if (!d) return;
      lastWheel = now;
      turnPages(d);
    },
    { passive: false, ...sig },
  );

  let sx = -1;
  let sy = 0;
  stage.addEventListener(
    'touchstart',
    (e) => {
      if (e.touches.length !== 1) sx = -1;
      else {
        sx = (e.touches[0] as Touch).clientX;
        sy = (e.touches[0] as Touch).clientY;
      }
    },
    { passive: true, ...sig },
  );
  stage.addEventListener(
    'touchend',
    (e) => {
      if (sx < 0 || e.changedTouches.length !== 1 || selecting()) return;
      const t = e.changedTouches[0] as Touch;
      const dx = t.clientX - sx;
      const dy = t.clientY - sy;
      const start = sx;
      sx = -1;
      if (paged()) {
        const d = pageSwipe(dx, dy);
        if (d) turnPages(d);
      } else {
        const d = chapterSwipe(dx, dy, start, window.innerWidth);
        if (d) go(idx + d, d < 0);
      }
    },
    { passive: true, ...sig },
  );

  window.addEventListener(
    'pointermove',
    (e) => {
      if (e.pointerType === 'mouse' && e.clientY < 64) showChrome();
    },
    { passive: true, ...sig },
  );

  // ------------------------------------------------------------ buttons
  function moreSheet(): void {
    const items: [string, string, SafeHtml][] = [
      ['mark', 'Đánh dấu đoạn này', icon('bookmark')],
      ['marks', 'Danh sách đánh dấu', icon('list')],
      ...(paged() ? [] : ([['auto', auto.running ? 'Dừng tự cuộn' : 'Tự cuộn', xicon('autoScroll')]] as [string, string, SafeHtml][])),
      ['settings', 'Cài đặt đọc', icon('settings')],
      ['menu', 'Danh mục truyện', icon('menu')],
      ['help', 'Phím tắt', xicon('help')],
    ];
    const d: DialogHandle = openDialog({
      title: 'Thêm',
      variant: 'sheet',
      className: 'rd-more-dialog',
      body: html`<ul class="rd-more">${items.map(([a, t, ic]) => html`<li><button type="button" class="rd-more-item" data-more="${a}">${ic}<span>${t}</span></button></li>`)}</ul>`,
    });
    d.body.addEventListener('click', (e) => {
      const b = (e.target as Element).closest<HTMLElement>('[data-more]');
      if (!b) return;
      const a = b.dataset.more as string;
      d.close();
      later(() => act(a), 30);
    });
  }

  function drawer(tab: DrawerTab = 'toc'): void {
    openChapterDrawer({ st, idx, tab });
  }

  function act(a: string): void {
    switch (a) {
      case 'prev':
        return go(idx - 1, paged());
      case 'next':
        return go(idx + 1);
      case 'toc':
        return drawer('toc');
      case 'marks':
        return drawer('marks');
      case 'mark':
        return toggleMark();
      case 'auto':
        return toggleAuto();
      case 'auto-slower':
        return auto.nudge(-1);
      case 'auto-faster':
        return auto.nudge(1);
      case 'auto-stop':
        return auto.stop();
      case 'listen':
        return void listen();
      case 'settings':
        return openSettings();
      case 'help':
        return openHelp();
      case 'more':
        return moreSheet();
      case 'menu':
        return shell.openDrawer();
    }
  }

  el.addEventListener(
    'click',
    (e) => {
      const b = (e.target as Element).closest<HTMLElement>('[data-act]');
      if (b && el.contains(b)) act(b.dataset.act as string);
    },
    sig,
  );
  chrome.addEventListener('pointerenter', () => showChrome(), sig);
  chrome.addEventListener('focusin', () => root.classList.remove('rd-hide'), sig);
  // links at the end of the chapter replace the history entry like the buttons do
  for (const a of el.querySelectorAll<HTMLAnchorElement>('[data-end-nav]')) {
    a.addEventListener(
      'click',
      (e) => {
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
        e.preventDefault();
        go(idx + (a.dataset.endNav === 'next' ? 1 : -1), a.dataset.endNav === 'prev' && paged());
      },
      sig,
    );
  }

  // ------------------------------------------------------------ keyboard
  document.addEventListener(
    'keydown',
    (e) => {
      if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey || e.isComposing) return;
      if (typingTarget(e) && !(e.key === 'Escape')) return;
      if (overlayOpen()) return;
      const k = keyOf(e);
      // WCAG 2.1.4: letters, Space, ? and +/- only work while "Phím tắt một phím" is on (default); arrows and Escape always do
      if (!shortcutAllowed(e, S.shortcuts, SINGLE_KEYS.has(k))) {
        if (k === ' ') auto.hold(1500);
        return;
      }
      const listening = document.getElementById('player-dock')?.childElementCount ? playing || !!currentMark() : false;
      let used = true;
      if (k === 'ArrowLeft' || k === 'ArrowRight') {
        const d = k === 'ArrowRight' ? 1 : -1;
        if (e.shiftKey) {
          if (listening) return; // the player dock owns Shift+arrows while it is active
          go(idx + d, d < 0 && paged());
        } else if (paged()) turnPages(d);
        else go(idx + d, false);
      } else if (k === 'PageDown' && paged()) turnPages(1);
      else if (k === 'PageUp' && paged()) turnPages(-1);
      else if (k === 'Home' && paged()) setPage(0);
      else if (k === 'End' && paged()) setPage(pages - 1);
      else if (k === 'm') drawer('toc');
      else if (k === 'b') toggleMark();
      else if (k === 'a') toggleAuto();
      else if ((k === '+' || k === '=') && auto.running) auto.nudge(1);
      else if ((k === '-' || k === '_') && auto.running) auto.nudge(-1);
      else if (k === '?') openHelp();
      else if (k === 'Escape') {
        if (auto.running) auto.stop();
        else toggleChrome();
      } else if (k === ' ' && !e.shiftKey && !listening) void listen();
      else used = false;
      if (used) {
        e.preventDefault();
        if (k !== 'Escape') showChrome();
      } else if (k === 'ArrowUp' || k === 'ArrowDown' || k === 'PageUp' || k === 'PageDown' || k === ' ') auto.hold(1500);
    },
    sig,
  );

  // ------------------------------------------------------------ settings, resize, lifecycle
  const reflow = debounce(() => {
    if (ac.signal.aborted) return;
    relayout(lastAnchor);
    void document.fonts?.ready.then(() => !ac.signal.aborted && !selecting() && relayout(lastAnchor));
  }, 60);
  subs.push(
    settings.onChange((key) => {
      if (key === null || ['readMode', 'size', 'line', 'width', 'font', 'weight', 'letter', 'word', 'align', 'indent', 'paraGap', 'margin', 'theme'].includes(key as string)) reflow();
    }),
  );
  subs.push(on('bookmarks', markSync));

  let rw = 0;
  let rh = 0;
  if (typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(() => {
      if (!paged()) return;
      const w = Math.floor(clip.clientWidth);
      const h = Math.floor(clip.clientHeight);
      if (Math.abs(w - rw) < 1 && Math.abs(h - rh) < 1) return;
      rw = w;
      rh = h;
      reflow();
    });
    ro.observe(clip);
    subs.push(() => ro.disconnect());
  }

  const flushNow = (): void => savePos(true, true);
  window.addEventListener('pagehide', flushNow, sig);
  document.addEventListener('visibilitychange', () => document.visibilityState === 'hidden' && flushNow(), sig);

  // ------------------------------------------------------------ opening position
  ctx.setTitle(`${label} · ${st.name}`);
  const start = startPosition({
    queryPara: c.route.query.p,
    atEnd: c.route.query.end === '1',
    saved: progress.get(st.source, st.key),
    idx,
    chapters: st.chapters,
    count: paras.length,
  });
  applyMode();
  window.scrollTo(0, 0);
  if (paged()) {
    layoutPages();
    setPage(start.end ? pages - 1 : pageFor(start));
  } else {
    restoreScroll(start, start.end ? 'end' : start.para === 0 && start.frac === 0 && !start.explicit ? 'top' : 'line');
  }
  lastAnchor = start;
  lastY = window.scrollY;
  const root2 = document.scrollingElement || document.documentElement;
  frac = scrollFraction(window.scrollY, root2.scrollHeight, window.innerHeight);
  ready = true;
  updateUi();
  savePos(true);
  markSync();
  syncListen('idle');
  if (start.explicit && (c.route.query.p != null || c.route.query.end != null)) setQuery({ p: null, end: null });
  if (!auto.running) later(hideChrome, HIDE_AFTER);

  // fonts and late layout move the text: put the same position back unless the reader already moved
  const settle = (): void => {
    if (ac.signal.aborted || performance.now() - userAt < 1500 || userAt > 0) return;
    relayout(start.end ? { para: paras.length - 1, frac: 0 } : lastAnchor);
    if (start.end && !paged()) restoreScroll(start, 'end');
  };
  void document.fonts?.ready.then(() => {
    settle();
    ignoreScrollUntil = performance.now() + 300;
  });

  // next-chapter prefetch
  const nextRef = st.chapters[idx + 1];
  if (nextRef) {
    later(() => {
      if (!ac.signal.aborted) data.chapter(st.source, st.key, nextRef.file).catch(() => {});
    }, 1200);
  }

  live = {
    goto(route) {
      const q = route.query.p;
      if (q == null || q === '') return;
      gotoPara(Number(q));
      setQuery({ p: null });
    },
  };

  teardown = () => {
    ready && savePos(true);
    ready = false;
    ac.abort();
    saveSoon.cancel();
    reflow.cancel();
    if (rafScroll) cancelAnimationFrame(rafScroll);
    for (const t of timers) clearTimeout(t);
    timers.clear();
    for (const u of subs) u();
    auto.stop();
    hl.clear();
    closeChapterDrawer();
  };
}

export async function mount(el: HTMLElement, route: Route, ctx: ViewContext): Promise<void> {
  teardown?.();
  teardown = null;
  const source = route.source as string;
  const key = route.key as string;
  ctx.setTitle('Đang mở chương');
  render(el, html`<div class="rd rd-loading"><h1 class="sr-only">Đang mở chương</h1><div class="rd-clip"><div class="rd-article">${skeleton.view(skeleton.lines(12))}</div></div></div>`);
  try {
    const st0 = await data.story(source, key, { signal: ctx.signal });
    if (ctx.signal.aborted) return;
    const st: StoryDetail = { ...st0, source: st0.source || source, key: st0.key || key };
    const idx = Math.min(st.chapters.length - 1, Math.max(0, route.idx ?? 0));
    const ref = st.chapters[idx];
    if (!ref) throw new Error('Truyện này chưa có chương nào');
    const ch = await data.chapter(source, key, ref.file, { signal: ctx.signal });
    if (ctx.signal.aborted) return;
    const label = chapterLabel({ ...ref, title: ref.title || ch.title || '' });
    open({ el, ctx, st, idx, ref, ch, label, route });
  } catch (e) {
    if (isAbort(e) || ctx.signal.aborted) return;
    ctx.setTitle('Không tải được chương');
    showError(el, e, () => {
      data.invalidate('chapter:');
      void mount(el, route, ctx);
    });
  }
}

export function update(route: Route): void {
  live?.goto(route);
}

export function unmount(): void {
  teardown?.();
  teardown = null;
  live = null;
}
