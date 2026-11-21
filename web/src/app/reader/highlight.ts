/**
 * Marks the sentence the player is speaking inside a paragraph. A paragraph is a single text node; the
 * highlighter splits it into "before", `<mark class="rd-say">` and "after" and puts the plain text back when
 * the voice moves on, so at most one paragraph of the chapter ever holds extra nodes.
 */

export interface Highlighter {
  /** Marks characters [s, e) of paragraph `para` (-1 = the title). Returns the marked element, or null. */
  set(para: number, s: number, e: number): HTMLElement | null;
  clear(): void;
}

export function createHighlighter(o: {
  /** Element of a paragraph, or null when it does not exist. */
  paraEl(i: number): HTMLElement | null;
  /** Source text of a paragraph (what the offsets refer to). */
  paraText(i: number): string;
  titleEl: HTMLElement | null;
}): Highlighter {
  let lastPara: number | null = null;

  function restore(): void {
    if (lastPara === null) return;
    if (lastPara < 0) o.titleEl?.classList.remove('rd-say');
    else {
      const el = o.paraEl(lastPara);
      if (el) {
        el.textContent = o.paraText(lastPara);
        el.classList.remove('rd-saying');
      }
    }
    lastPara = null;
  }

  return {
    set(para, s, e) {
      if (para < 0) {
        if (lastPara !== -1) restore();
        if (!o.titleEl) return null;
        o.titleEl.classList.add('rd-say');
        lastPara = -1;
        return o.titleEl;
      }
      const el = o.paraEl(para);
      if (!el) {
        restore();
        return null;
      }
      if (lastPara !== para) restore();
      const text = o.paraText(para);
      const a = Math.max(0, Math.min(text.length, Math.trunc(s) || 0));
      const b = Math.max(a, Math.min(text.length, Math.trunc(e) || 0));
      lastPara = para;
      el.classList.add('rd-saying');
      if (b <= a) {
        el.textContent = text;
        return el;
      }
      const mark = document.createElement('mark');
      mark.className = 'rd-say';
      mark.textContent = text.slice(a, b);
      const nodes: Node[] = [];
      if (a > 0) nodes.push(document.createTextNode(text.slice(0, a)));
      nodes.push(mark);
      if (b < text.length) nodes.push(document.createTextNode(text.slice(b)));
      el.replaceChildren(...nodes);
      return mark;
    },
    clear: restore,
  };
}
