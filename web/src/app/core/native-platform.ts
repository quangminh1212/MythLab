/**
 * Which Capacitor shell we are in. `Capacitor.getPlatform()` is 'android' | 'ios' | 'web'.
 * Kept apart from settings.ts (isNative) and platform.ts (user-agent sniffing for the Safari PWA): inside the
 * iOS app the user agent is also iPhone, but the native plugins and what they can do differ from Android.
 * A bridge without getPlatform (older shell, tests) counts as Android, the shell this code was written for.
 */
import { isNative } from './settings';

export type NativePlatform = 'android' | 'ios' | 'web';

export function nativePlatform(): NativePlatform {
  try {
    if (!isNative()) return 'web';
    const c = (globalThis as { Capacitor?: { getPlatform?: () => string } }).Capacitor;
    const p = typeof c?.getPlatform === 'function' ? c.getPlatform() : 'android';
    return p === 'ios' ? 'ios' : p === 'web' ? 'web' : 'android';
  } catch {
    return 'web';
  }
}

/** True inside the Capacitor iOS app (not Safari / the installed PWA). */
export const isNativeIOS = (): boolean => nativePlatform() === 'ios';

/**
 * Google OAuth client id of type "iOS", read from `<meta name="mythlab-ios-google-client-id">`
 * (apps/ios/sync-web.mjs writes it from IOS_GOOGLE_CLIENT_ID). It is public, not a secret. Empty when absent.
 */
export function iosGoogleClientId(doc: Pick<Document, 'querySelector'> | undefined = typeof document === 'undefined' ? undefined : document): string {
  try {
    const v = doc?.querySelector('meta[name="mythlab-ios-google-client-id"]')?.getAttribute('content')?.trim() ?? '';
    return /^[\w.-]+\.apps\.googleusercontent\.com$/.test(v) ? v : '';
  } catch {
    return '';
  }
}
