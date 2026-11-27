/** iOS / iPadOS detection. iPadOS 13+ reports itself as a Mac ("MacIntel", desktop user agent), told apart by touch points. */
interface Env {
  userAgent?: string;
  platform?: string;
  maxTouchPoints?: number;
}

const env = (): Env => (typeof navigator === 'undefined' ? {} : (navigator as Env));

/** True on iPhone, iPod and iPad (including iPadOS in desktop mode). Any browser there is WebKit. */
export function isIOS(n: Env = env()): boolean {
  const ua = n.userAgent ?? '';
  if (/iPad|iPhone|iPod/.test(ua)) return true;
  return (n.platform === 'MacIntel' || /Macintosh/.test(ua)) && (n.maxTouchPoints ?? 0) > 1;
}

/** True in Safari proper on iOS (not Chrome / Firefox / Edge / in-app browsers, which cannot "Add to Home Screen" the same way). */
export function isIosSafari(n: Env = env()): boolean {
  if (!isIOS(n)) return false;
  const ua = n.userAgent ?? '';
  return !/CriOS|FxiOS|EdgiOS|OPiOS|GSA\/|FBAN|FBAV|Instagram|Line\//.test(ua);
}
