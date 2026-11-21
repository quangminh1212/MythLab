/**
 * Story covers: an instant generated SVG placeholder (stable per story: hue from the name, motif from the genre,
 * the title set in the display serif) with the real image layered on top once it has loaded.
 */
import { backend } from './backend/index';
import type { CoverRef } from './backend/types';
import { hashHue, normTxt } from './format';
import { esc, html, raw, type SafeHtml } from './html';

const MOTIFS: [RegExp, string][] = [
  [/tien hiep|huyen huyen|tu chan|tu tien|kiem hiep|vo hiep|co dai|cung dau|dong phuong/, 'M0 250 L45 185 L75 215 L110 160 L150 210 L175 190 L200 225 V300 H0Z M20 300 L70 232 L100 258 L135 222 L200 280 M145 95 a24 24 0 1 0 .1 0'],
  [/lich su|quan su|quan truong|chien tranh|binh/, 'M100 300 V170 M100 170 L60 150 M100 170 L140 150 M100 170 L72 120 M100 170 L128 120 M100 170 V105 M30 260 H170 M45 280 H155'],
  [/mat the|khoa huyen|vong du|he thong|tro choi|game|tuong lai|vu tru/, 'M100 150 l48 28 v56 l-48 28 l-48 -28 v-56z M100 178 l24 14 v28 l-24 14 l-24 -14 v-28z M100 150 V120 M148 178 l26 -15 M52 178 l-26 -15 M148 234 l26 15 M52 234 l-26 15 M100 262 V292'],
  [/ngon tinh|dam my|sung|hon nhan|tinh yeu|lang man|nu cuong|nu ton/, 'M100 235 c-30 -22 -52 -40 -52 -62 a26 26 0 0 1 52 -6 a26 26 0 0 1 52 6 c0 22 -22 40 -52 62z M40 120 a8 8 0 1 0 .1 0 M165 135 a6 6 0 1 0 .1 0 M150 268 a5 5 0 1 0 .1 0'],
  [/linh di|kinh di|trinh tham|huyen bi|ma |quy|lieu trai/, 'M130 120 a50 50 0 1 0 0 80 a40 40 0 1 1 0 -80z M40 250 h120 M55 268 h90 M30 140 l4 -8 l4 8 M165 230 l3 -6 l3 6'],
  [/am thuc|nau an|my thuc|thuong gia|kinh doanh|nien dai|lam ruong|dien van/, 'M45 210 h110 a55 55 0 0 1 -110 0z M75 190 c-8 -14 8 -22 0 -36 M100 190 c-8 -14 8 -22 0 -36 M125 190 c-8 -14 8 -22 0 -36 M80 280 h40'],
  [/co tich|dong thoai|thieu nhi|truyen thuyet|than thoai|ngu ngon|dan gian/, 'M100 140 l8 24 l24 0 l-19 15 l7 24 l-20 -15 l-20 15 l7 -24 l-19 -15 l24 0z M45 230 l4 10 l10 0 l-8 6 l3 10 l-9 -6 l-9 6 l3 -10 l-8 -6 l10 0z M155 215 l3 8 l8 0 l-6 5 l2 8 l-7 -5 l-7 5 l2 -8 l-6 -5 l8 0z'],
  [/do thi|hien dai|vuon truong|hao mon|showbiz|giai tri|the thao/, 'M10 300 V240 h25 V210 h22 V250 h18 V190 h30 V235 h20 V215 h25 V255 h20 V230 h20 V300 M40 225 h8 M100 205 h10 M100 220 h10'],
];
const DEF_MOTIF = 'M0 230 q50 -30 100 0 t100 0 M0 255 q50 -30 100 0 t100 0 M0 280 q50 -30 100 0 t100 0';

/** Breaks a title into lines that fit the 200x300 cover, choosing the largest font size that works. */
export function wrapTitle(title: string): { fs: number; lines: string[] } {
  const t = String(title || '').trim();
  const sizes: [number, number][] = [
    [27, 3],
    [23, 4],
    [19, 4],
    [16, 5],
    [14, 6],
  ];
  for (const [fs, maxL] of sizes) {
    const per = Math.floor(168 / (fs * 0.5));
    const lines: string[] = [];
    let cur = '';
    for (const w of t.split(/\s+/)) {
      if (!cur) cur = w;
      else if ((cur + ' ' + w).length <= per) cur += ' ' + w;
      else {
        lines.push(cur);
        cur = w;
      }
    }
    if (cur) lines.push(cur);
    if (lines.length <= maxL && lines.every((l) => l.length <= per + 1)) return { fs, lines };
    if (fs === 14) {
      return {
        fs,
        lines: lines.slice(0, maxL).map((l, i) => {
          const cut = l.length > per + 1 || (i === maxL - 1 && lines.length > maxL);
          return cut ? l.slice(0, per - 1) + '…' : l;
        }),
      };
    }
  }
  return { fs: 14, lines: [t] };
}

/** What a cover needs to know about a story. StorySummary, StoryDetail, Progress and Follow all fit. */
export interface CoverStory extends CoverRef {
  name: string;
  folder?: string;
  author?: string | null;
  genres?: string[];
  tags?: string[];
  group?: string | null;
  repo?: string | null;
}

/** Background colour of the generated cover (also used as the placeholder tint). */
export const coverHue = (st: { name: string; folder?: string }): number => hashHue(st.name || st.folder || '');

/** The generated cover as SVG markup. Every dynamic part is escaped or numeric. */
export function genCover(st: CoverStory, mark = 'MythLab'): SafeHtml {
  const name = st.name || st.folder || '';
  const h = coverHue(st);
  const group = (st.group || st.repo || '').replace(/^Done_/, '').replace(/([a-z])([A-Z])/g, '$1 $2');
  const topic = normTxt([...(st.genres || []), ...(st.tags || []).slice(0, 4), group].join(' | '));
  const motif = MOTIFS.find(([re]) => re.test(topic))?.[1] ?? DEF_MOTIF;
  const { fs, lines } = wrapTitle(name);
  const lh = fs * 1.16;
  const y0 = 112 - ((lines.length - 1) * lh) / 2;
  const author = st.author ? String(st.author).slice(0, 34) : '';
  const tspans = lines.map((l, i) => `<tspan x="100" dy="${i ? lh.toFixed(1) : 0}">${esc(l)}</tspan>`).join('');
  return raw(
    `<svg class="gc" viewBox="0 0 200 300" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">` +
      `<rect width="200" height="300" fill="hsl(${h} 42% 24%)"/>` +
      `<path d="${motif}" fill="none" stroke="hsl(${(h + 40) % 360} 70% 80%)" stroke-opacity=".22" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>` +
      `<rect x="12" y="12" width="176" height="276" rx="3" fill="none" stroke="hsl(42 70% 75%)" stroke-opacity=".35"/>` +
      `<path d="M78 262 H122" stroke="hsl(42 70% 75%)" stroke-opacity=".5"/>` +
      `<text x="100" y="278" text-anchor="middle" font-family="Inter, sans-serif" font-size="8.5" font-weight="700" letter-spacing="3" fill="hsl(42 75% 78%)" fill-opacity=".85">${esc(mark.toUpperCase())}</text>` +
      `<text x="100" y="${y0.toFixed(1)}" text-anchor="middle" font-family="Alegreya, 'Noto Serif', Georgia, serif" font-weight="800" font-size="${fs}" fill="#fdf8ec" paint-order="stroke" stroke="rgba(0,0,0,.25)" stroke-width="2">${tspans}</text>` +
      (author ? `<text x="100" y="248" text-anchor="middle" font-family="Inter, sans-serif" font-size="10" fill="#fdf8ec" fill-opacity=".8">${esc(author)}</text>` : '') +
      `</svg>`,
  );
}

// ---------------------------------------------------------------- real images

let seq = 0;
/** Covers waiting for an authenticated fetch (GitHub blob, keyed server), by element id. */
const waiting = new Map<string, { st: CoverRef; w: number }>();
let io: IntersectionObserver | null = null;

function reveal(img: HTMLImageElement): void {
  if (img.complete && img.naturalWidth > 0) img.classList.add('ok');
  else {
    img.addEventListener('load', () => img.classList.add('ok'), { once: true });
    img.addEventListener('error', () => img.remove(), { once: true });
  }
}

function loadDeferred(box: HTMLElement): void {
  const id = box.dataset.cover || '';
  const job = waiting.get(id);
  waiting.delete(id);
  delete box.dataset.cover;
  if (!job) return;
  let p: string | Promise<string> | null;
  try {
    p = backend.coverUrl(job.st, job.w);
  } catch {
    return;
  }
  if (!p) return;
  Promise.resolve(p).then(
    (url) => {
      if (!url || !box.isConnected) return;
      const img = document.createElement('img');
      img.className = 'cover-img';
      img.alt = '';
      img.decoding = 'async';
      img.src = url;
      box.appendChild(img);
      reveal(img);
    },
    () => {},
  );
}

/**
 * Markup of a cover box: the generated SVG plus, when the story has an image, an `<img>` that fades in on load
 * (and removes itself on error, leaving the placeholder). `w` is the displayed CSS width (picks the server
 * variant). Call {@link hydrateCovers} on the container after inserting the markup.
 */
export function cover(st: CoverStory, o: { w?: number; cls?: string; eager?: boolean } = {}): SafeHtml {
  const w = o.w ?? 160;
  const cls = o.cls && /^[\w -]*$/.test(o.cls) ? ' ' + o.cls : '';
  let src: string | Promise<string> | null = null;
  try {
    src = backend.coverUrl(st, w);
  } catch {
    src = null;
  }
  if (typeof src === 'string' && src) {
    return html`<div class="cover${raw(cls)}">${genCover(st)}<img class="cover-img" src="${src}" alt="" loading="${o.eager ? 'eager' : 'lazy'}" decoding="async" referrerpolicy="no-referrer" /></div>`;
  }
  if (src) {
    const id = 'c' + ++seq;
    waiting.set(id, { st: { key: st.key, cover: st.cover, poster: st.poster, cover_sha: st.cover_sha }, w });
    // keep the wait list bounded when views are replaced before their covers were hydrated
    if (waiting.size > 600) waiting.delete(waiting.keys().next().value as string);
    return html`<div class="cover${raw(cls)}" data-cover="${id}">${genCover(st)}</div>`;
  }
  return html`<div class="cover${raw(cls)}">${genCover(st)}</div>`;
}

/** Wires the covers inside `root`: fade-in/onerror for plain images, lazy authenticated loading for the rest. */
export function hydrateCovers(root: ParentNode = document): void {
  for (const img of Array.from(root.querySelectorAll<HTMLImageElement>('img.cover-img:not(.ok)'))) reveal(img);
  const boxes = Array.from(root.querySelectorAll<HTMLElement>('[data-cover]'));
  if (!boxes.length) return;
  if (typeof IntersectionObserver === 'undefined') {
    boxes.forEach(loadDeferred);
    return;
  }
  io ??= new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        io?.unobserve(e.target);
        loadDeferred(e.target as HTMLElement);
      }
    },
    { rootMargin: '300px' },
  );
  for (const b of boxes) io.observe(b);
}
