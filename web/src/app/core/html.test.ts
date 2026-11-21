import { describe, expect, it } from 'vitest';
import { cssVars, esc, fragment, html, join, raw, render, SafeHtml } from './html';

describe('html helper', () => {
  it('escapes every interpolated string', () => {
    const evil = '<img src=x onerror="alert(1)">\'`';
    const out = html`<p title="${evil}">${evil}</p>`.s;
    expect(out).not.toContain('<img');
    expect(out).toContain('&lt;img src=x onerror=&quot;alert(1)&quot;&gt;&#39;&#96;');
    expect(esc('a & b')).toBe('a &amp; b');
  });

  it('keeps nested templates and raw() as markup, and escapes strings inside arrays', () => {
    const items = ['<b>x</b>', html`<i>y</i>`, raw('<u>z</u>')];
    expect(html`<ul>${items}</ul>`.s).toBe('<ul>&lt;b&gt;x&lt;/b&gt;<i>y</i><u>z</u></ul>');
    expect(join(['a<', html`<br>`], raw(', ')).s).toBe('a&lt;, <br>');
  });

  it('renders nothing for null, undefined and booleans, and numbers as text', () => {
    expect(html`[${null}${undefined}${false}${true}${0}]`.s).toBe('[0]');
  });

  it('an object that only looks like SafeHtml is still escaped', () => {
    const fake = { s: '<script>1</script>', toString: () => '<script>1</script>' } as unknown as string;
    expect(html`${fake}`.s).not.toContain('<script>');
    expect(new SafeHtml('<b>').toString()).toBe('<b>');
  });

  it('render() puts escaped data in the DOM as text', () => {
    const el = document.createElement('div');
    const name = '<script>window.x=1</script>';
    render(el, html`<a href="${'" onclick="x'}">${name}</a>`);
    const a = el.querySelector('a') as HTMLAnchorElement;
    expect(el.querySelector('script')).toBeNull();
    expect(a.textContent).toBe(name);
    expect(a.getAttribute('href')).toBe('" onclick="x');
    expect(a.hasAttribute('onclick')).toBe(false);
    expect(fragment(html`<p>a</p><p>b</p>`).childNodes.length).toBe(2);
  });

  it('cssVars only lets custom properties with plain values through', () => {
    expect(cssVars({ '--h': 120, '--w': '50%', color: 'red', '--x': 'url(javascript:1);', '--n': null })).toBe('--h:120;--w:50%;');
  });
});
