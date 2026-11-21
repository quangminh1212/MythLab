/**
 * The only way dynamic markup reaches the DOM.
 *
 *   render(el, html`<a href="${url}">${title}</a>`)
 *
 * Every interpolated value is HTML-escaped unless it is already a SafeHtml (a nested html`` result, raw(), or an
 * array of those). The same escaping is correct for text content and for double- or single-quoted attribute values,
 * so ALWAYS quote attributes. Never assign `innerHTML` with interpolated data anywhere else (bugs.md S8).
 */

const ESC: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '`': '&#96;' };

/** Escapes text for HTML text nodes and quoted attribute values. */
export function esc(v: unknown): string {
  return String(v ?? '').replace(/[&<>"'`]/g, (c) => ESC[c] as string);
}

/** Markup that is already safe to insert. Only html``, raw() and join() create it. */
export class SafeHtml {
  readonly s: string;
  constructor(s: string) {
    this.s = s;
  }
  toString(): string {
    return this.s;
  }
}

export type HtmlValue = SafeHtml | string | number | boolean | null | undefined | HtmlValue[];

function part(v: HtmlValue): string {
  if (v instanceof SafeHtml) return v.s;
  if (v == null || v === false || v === true) return '';
  if (Array.isArray(v)) {
    let out = '';
    for (const x of v) out += part(x);
    return out;
  }
  return esc(v);
}

/** Tagged template: escapes every interpolation that is not SafeHtml; null/undefined/booleans render nothing. */
export function html(strings: TemplateStringsArray, ...values: HtmlValue[]): SafeHtml {
  let out = strings[0] as string;
  for (let i = 0; i < values.length; i++) out += part(values[i]) + (strings[i + 1] as string);
  return new SafeHtml(out);
}

/**
 * Marks a string as trusted markup. Use only for constants written in this code base (icons, generated SVG whose
 * dynamic parts were escaped). Never pass server or user data.
 */
export function raw(trusted: string): SafeHtml {
  return new SafeHtml(trusted);
}

/** Joins fragments (escaping plain strings) with an optional safe separator. */
export function join(items: HtmlValue[], sep: SafeHtml | '' = ''): SafeHtml {
  return new SafeHtml(items.map(part).join(sep instanceof SafeHtml ? sep.s : ''));
}

/** Replaces the children of `el` with safe markup. */
export function render(el: Element, content: SafeHtml): void {
  el.innerHTML = content.s;
}

/** Appends safe markup to `el` without re-parsing its existing children. */
export function append(el: Element, content: SafeHtml): void {
  el.insertAdjacentHTML('beforeend', content.s);
}

/** Builds a detached fragment from safe markup. */
export function fragment(content: SafeHtml): DocumentFragment {
  const t = document.createElement('template');
  t.innerHTML = content.s;
  return t.content;
}

/** Inline `style` value made of CSS custom properties; names and values are restricted to a safe character set. */
export function cssVars(vars: Record<string, string | number | null | undefined>): string {
  let out = '';
  for (const [k, v] of Object.entries(vars)) {
    if (v == null || !/^--[\w-]+$/.test(k)) continue;
    const val = String(v);
    if (!/^[\w\s.,%#()+\-/]*$/.test(val)) continue;
    out += `${k}:${val};`;
  }
  return out;
}

export const $ = <T extends Element = HTMLElement>(sel: string, root: ParentNode = document): T | null =>
  root.querySelector<T>(sel);
export const $$ = <T extends Element = HTMLElement>(sel: string, root: ParentNode = document): T[] =>
  Array.from(root.querySelectorAll<T>(sel));
