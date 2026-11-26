// @vitest-environment happy-dom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { S, set } from '../core/settings';
vi.mock('./voice', () => ({ mountVoice: () => () => {} }));
import { groupSummary, settingsPanel, visibleTabs } from './panel';

const q = <T extends Element = HTMLElement>(sel: string): T => document.querySelector(sel) as T;
const expanded = (): string[] => [...document.querySelectorAll<HTMLElement>('.ss-group-btn[aria-expanded="true"]')].map((b) => b.dataset.tab as string);
const visiblePanes = (): string[] => [...document.querySelectorAll<HTMLElement>('.ss-pane:not([hidden])')].map((p) => p.id);

describe('settings menu (accordion)', () => {
  afterEach(() => settingsPanel.close());

  it('renders one disclosure row per visible group, with one open at a time', () => {
    settingsPanel.open('layout');
    const rows = [...document.querySelectorAll<HTMLElement>('.ss-group-btn')];
    expect(rows.map((r) => r.dataset.tab)).toEqual(visibleTabs().map((t) => t.id));
    for (const r of rows) {
      expect(r.getAttribute('aria-controls')).toBe(`ss-pane-${r.dataset.tab}`);
      expect(document.getElementById(`ss-pane-${r.dataset.tab}`)?.getAttribute('aria-labelledby')).toBe(r.id);
    }
    expect(document.querySelector('[role="tab"], [role="tablist"]')).toBeNull();
    expect(expanded()).toEqual(['layout']);
    expect(visiblePanes()).toEqual(['ss-pane-layout']);
  });

  it('click expands one group (closing the other) and clicking again collapses it', () => {
    settingsPanel.open('theme');
    q('#ss-tab-font').click();
    expect(expanded()).toEqual(['font']);
    expect(visiblePanes()).toEqual(['ss-pane-font']);
    q('#ss-tab-font').click();
    expect(expanded()).toEqual([]);
    expect(visiblePanes()).toEqual([]);
  });

  it('open(tab) on an open sheet expands that group without toggling it off', () => {
    settingsPanel.open('theme');
    settingsPanel.open('voice');
    settingsPanel.open('voice');
    expect(expanded()).toEqual(['voice']);
  });

  it('fires settings-tab so lazy groups mount when first expanded', () => {
    settingsPanel.open('theme');
    const seen: string[] = [];
    q('.ss-panel').addEventListener('settings-tab', (e) => seen.push((e as CustomEvent<string>).detail));
    q('#ss-tab-source').click();
    expect(seen).toEqual(['source']);
  });

  it('shows short value summaries', () => {
    set('readMode', 'page');
    expect(groupSummary('layout')).toBe('Lật trang');
    set('readMode', 'scroll');
    expect(groupSummary('layout')).toBe('Cuộn dọc');
    expect(groupSummary('font')).toContain(`${S.size} px`);
    expect(groupSummary('source')).toBe('');
  });
});
