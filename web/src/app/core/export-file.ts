/**
 * Saving a text file and copying text in places where the browser way can silently do nothing.
 * A blob `<a download>` click works in a desktop browser, but the Android WebView (Capacitor) ignores it, and the
 * async Clipboard API can be denied there. Order tried by saveTextFile():
 *   1. Capacitor Filesystem + Share plugins, when the app bundles them (the file is written to cache and shared)
 *   2. a native `FileShare` plugin (see apps/android/PARITY_NOTES.md), when the app has one
 *   3. Web Share with a file, where the platform supports it (mobile browsers)
 *   4. the `<a download>` click, in a browser that is not the native shell
 *   5. otherwise 'manual': the caller shows the text so the user can copy it
 */
import { isNative } from './settings';

export type SaveResult = 'saved' | 'shared' | 'manual';

interface Plugins {
  Filesystem?: { writeFile(o: { path: string; data: string; directory: string; encoding: string; recursive?: boolean }): Promise<{ uri?: string }> };
  Share?: { share(o: { title?: string; url?: string; dialogTitle?: string }): Promise<unknown> };
  FileShare?: { share(o: { name: string; text: string; mime: string }): Promise<unknown> };
}
const plugins = (): Plugins => (globalThis as { Capacitor?: { Plugins?: Plugins } }).Capacitor?.Plugins ?? {};

/** True when the user cancelled a share sheet (not an error). */
const aborted = (e: unknown): boolean => {
  const n = (e as { name?: string })?.name;
  const m = String((e as { message?: string })?.message ?? '');
  return n === 'AbortError' || /cancel/i.test(m);
};

export async function saveTextFile(name: string, text: string, mime = 'application/json'): Promise<SaveResult> {
  const p = plugins();
  if (p.Filesystem && p.Share) {
    try {
      const w = await p.Filesystem.writeFile({ path: name, data: text, directory: 'CACHE', encoding: 'utf8' });
      if (w?.uri) {
        await p.Share.share({ title: name, url: w.uri, dialogTitle: name });
        return 'shared';
      }
    } catch (e) {
      if (aborted(e)) return 'shared';
    }
  }
  if (p.FileShare) {
    try {
      await p.FileShare.share({ name, text, mime });
      return 'shared';
    } catch (e) {
      if (aborted(e)) return 'shared';
    }
  }
  try {
    const nav = navigator as Navigator & { canShare?: (d: ShareData) => boolean };
    const file = new File([text], name, { type: mime });
    if (typeof nav.share === 'function' && nav.canShare?.({ files: [file] })) {
      await nav.share({ files: [file], title: name });
      return 'shared';
    }
  } catch (e) {
    if (aborted(e)) return 'shared';
  }
  if (isNative()) return 'manual';
  const url = URL.createObjectURL(new Blob([text], { type: mime }));
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.rel = 'noopener';
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
  return 'saved';
}

/** Copies text: async Clipboard API first, then a hidden textarea + execCommand (works in more WebViews). */
export async function copyText(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // fall through
  }
  try {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;font-size:16px';
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, text.length);
    const ok = document.execCommand('copy');
    ta.remove();
    return ok;
  } catch {
    return false;
  }
}
