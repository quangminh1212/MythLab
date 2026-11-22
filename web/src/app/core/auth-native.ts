/**
 * Native Google sign-in (Android, Capacitor). The bridge exposes plugins on `Capacitor.Plugins`; `registerPlugin`
 * is absent in the WebView (the same gap as the media service), so the community plugin
 * `@capgo/capacitor-social-login` is read from `Capacitor.Plugins.SocialLogin`, defensively. Everything here is
 * optional: without the plugin `nativeAvailable()` is false and the web flow is used instead.
 *
 * The ID token's audience is the WEB client id (the plugin's `webClientId` = server `google_client_ids`).
 */
import { isNative } from './settings';

interface SocialLoginPlugin {
  initialize(o: { google: { webClientId: string } }): Promise<unknown>;
  login(o: { provider: 'google'; options: Record<string, unknown> }): Promise<{ result?: { idToken?: string | null } } | null>;
  logout?(o: { provider: 'google' }): Promise<unknown>;
}

export class NativeAuthCancelled extends Error {
  constructor() {
    super('cancelled');
    this.name = 'NativeAuthCancelled';
  }
}

function plugin(): SocialLoginPlugin | null {
  try {
    if (!isNative()) return null;
    const p = (globalThis as { Capacitor?: { Plugins?: Record<string, unknown> } }).Capacitor?.Plugins?.SocialLogin as SocialLoginPlugin | undefined;
    return p && typeof p.login === 'function' && typeof p.initialize === 'function' ? p : null;
  } catch {
    return null;
  }
}

/** Is the native Google sign-in plugin present in this shell? */
export const nativeAvailable = (): boolean => plugin() !== null;

let initializedFor = '';

/** Opens the system account picker and resolves the Google ID token. Rejects NativeAuthCancelled when dismissed. */
export async function nativeGoogleIdToken(webClientId: string): Promise<string> {
  const p = plugin();
  if (!p) throw new Error('no native sign-in plugin');
  try {
    if (initializedFor !== webClientId) {
      await p.initialize({ google: { webClientId } });
      initializedFor = webClientId;
    }
    const r = await p.login({ provider: 'google', options: {} });
    const token = r?.result?.idToken;
    if (typeof token !== 'string' || !token) throw new Error('no id token');
    return token;
  } catch (e) {
    const x = e as { message?: unknown; code?: unknown } | null;
    if (/cancel|dismiss|12501|user.*(denied|closed)/i.test(`${String(x?.message ?? '')} ${String(x?.code ?? '')}`)) throw new NativeAuthCancelled();
    throw e;
  }
}

/** Best effort: forgets the Google account chosen in the app so the next sign-in shows the picker. */
export async function nativeSignOut(): Promise<void> {
  try {
    await plugin()?.logout?.({ provider: 'google' });
  } catch {
    /* nothing to clear */
  }
}
