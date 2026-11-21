/** Markup shared by the browse views: story cards, continue-reading cards, repository tiles, section heads. */
import type { Progress, RepoInfo, StorySummary } from '../core/contracts';
import { cover, type CoverStory } from '../core/covers';
import { fmtDate, fmtNum, repoLabel } from '../core/format';
import { html, type SafeHtml } from '../core/html';
import { icon } from '../core/icons';
import { progress } from '../core/progress';
import { href } from '../core/router';

/** Chapter count of a story summary for display ('' when unknown). */
export function chapterCountText(s: Pick<StorySummary, 'chapter_files' | 'declared_chapters'>): string {
  const n = s.chapter_files ?? s.declared_chapters ?? 0;
  return n > 0 ? `${fmtNum(n)} chương` : '';
}

/** A story in a grid or shelf. `source` is the source the list came from (search items carry their own). */
export function storyCard(s: StorySummary, source: string, o: { showRepo?: boolean } = {}): SafeHtml {
  const src = s.source || source;
  const meta = [s.author || '', chapterCountText(s)].filter(Boolean).join(' · ');
  const repo = o.showRepo ? s.repo || s.group || '' : '';
  return html`<a class="card" href="${href.story(src, s.key)}" title="${s.name}">
    ${cover({ ...s, group: s.group ?? s.repo ?? null }, { w: 160 })}
    <span class="card-body">
      <span class="card-title">${s.name}</span>
      ${meta ? html`<span class="card-meta">${meta}</span>` : ''} ${repo ? html`<span class="card-meta card-repo">${repoLabel(repo)}</span>` : ''}
    </span>
  </a>`;
}

/** A story the reader has opened: links straight back into the reader at the saved chapter. */
export function continueCard(p: Progress): SafeHtml {
  const pct = progress.percent(p);
  const st: CoverStory = { key: p.key, name: p.name, author: p.author, genres: p.genres, group: p.group, cover: p.cover, poster: p.poster, cover_sha: p.cover_sha };
  const where = p.total ? `Chương ${fmtNum(p.n)} / ${fmtNum(p.total)}` : `Chương ${fmtNum(p.n)}`;
  return html`<a class="card card-continue" href="${href.read(p.source, p.key, p.idx)}" title="Đọc tiếp ${p.name}">
    ${cover(st, { w: 160 })}
    <span class="card-body">
      <span class="card-title">${p.name || p.key}</span>
      <span class="card-meta">${where}</span>
      <progress class="bar" max="100" value="${pct}" aria-label="Đã đọc ${pct}%"></progress>
    </span>
  </a>`;
}

/** A repository (a genre folder of a GitHub source). */
export function repoTile(source: string, r: RepoInfo): SafeHtml {
  const d = fmtDate(r.pushed_at);
  return html`<a class="tile" href="${href.lib(source, r.repo)}" title="${r.repo}">
    <span class="tile-ic">${icon('folder')}</span>
    <span class="tile-body"><span class="tile-title">${repoLabel(r.repo)}</span>${d ? html`<span class="tile-meta">Cập nhật ${d}</span>` : ''}</span>
  </a>`;
}

/** Section heading with an optional "Xem tất cả" link. `id` labels the section for assistive tech. */
export function sectionHead(o: { id: string; title: string; count?: number; more?: { href: string; label?: string; aria: string } }): SafeHtml {
  return html`<div class="section-head">
    <h2 id="${o.id}" class="section-title">${o.title}${o.count != null ? html` <span class="section-count">${fmtNum(o.count)}</span>` : ''}</h2>
    ${o.more ? html`<a class="more-link" href="${o.more.href}" aria-label="${o.more.aria}"><span>${o.more.label || 'Xem tất cả'}</span>${icon('right')}</a>` : ''}
  </div>`;
}

/** Page heading used by every browse view. */
export function pageHead(title: string, sub?: string, actions?: SafeHtml): SafeHtml {
  return html`<header class="page-head">
    <div class="page-head-text">
      <h1 class="page-title">${title}</h1>
      ${sub ? html`<p class="page-sub">${sub}</p>` : ''}
    </div>
    ${actions ? html`<div class="page-actions">${actions}</div>` : ''}
  </header>`;
}
