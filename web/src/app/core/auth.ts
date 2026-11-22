/**
 * "Sign in with Google": turns a Google ID token into a MythLab session (`POST /api/auth/google`), keeps it in
 * `core/auth-token.ts` and tells the sync modules through the 'auth' event. Everything is optional: the server
 * advertises it in /api/ping (`auth.google`), and without a session the app behaves exactly as before.
 *
 *   browser / desktop WebView2  Google Identity Services, loaded lazily the first time the button is shown
 *   Android                      the native account picker through `auth-native.ts`
 *
 * Signing out revokes the session on the server (best effort), forgets the token and stops syncing; the local
 * history, bookmarks and follows stay on the device.
 */
import { accountId, authToken, session, setSession, updateUser, type AuthUser } from './auth-token';
import { nativeAvailable, nativeGoogleIdToken, NativeAuthCancelled, nativeSignOut } from './auth-native';
import { backend } from './backend';
import { ApiError } from './backend/types';
import { Emitter, emit, on } from './events';

export const GSI_SRC = 'https://accounts.google.com/gsi/client';

interface GsiApi {
  accounts: {
    id: {
      initialize(o: Record<string, unknown>): void;
      renderButton(el: HTMLElement, o: Record<string, unknown>): void;
      disableAutoSelect(): void;
    };
  };
}
declare global {
  interface Window {
    google?: GsiApi;
  }
}

export type AuthErrorCode = 'cancelled' | 'bad_token' | 'not_allowed' | 'unavailable' | 'network';

export class AuthError extends Error {
  readonly code: AuthErrorCode;
  constructor(message: string, code: AuthErrorCode) {
    super(message);
    this.name = 'AuthError';
    this.code = code;
  }
}

interface LoginResponse {
  token: string;
  expires?: number;
  user: Partial<AuthUser>;
}

const base = (): string => backend.serverBase ?? '';

/** Does the active server offer Google sign-in? */
export const available = (): boolean => backend.kind === 'server' && !!backend.auth?.google;
/** Signed in on this server? */
export const signedIn = (): boolean => !!authToken(base());
export const user = (): AuthUser | null => (signedIn() ? (session()?.user ?? null) : null);
/** 'native' when the shell has its own account picker, otherwise 'web' (Google Identity Services). */
export const mode = (): 'native' | 'web' => (nativeAvailable() ? 'native' : 'web');

// ---------------------------------------------------------------- session

function toAuthError(e: unknown): AuthError {
  if (e instanceof AuthError) return e;
  if (e instanceof NativeAuthCancelled) return new AuthError('Bạn đã huỷ đăng nhập.', 'cancelled');
  if (e instanceof ApiError) {
    if (e.status === 403 || e.code === 'not_allowed') return new AuthError('Tài khoản Google này không được phép dùng máy chủ này.', 'not_allowed');
    if (e.status === 401 || e.code === 'bad_token') return new AuthError('Google không xác nhận được đăng nhập. Hãy thử lại.', 'bad_token');
    if (e.status === 404) return new AuthError('Máy chủ chưa bật đăng nhập Google.', 'unavailable');
    if (e.status === 429) return new AuthError('Thử quá nhiều lần. Hãy đợi một phút rồi thử lại.', 'network');
  }
  return new AuthError('Không đăng nhập được. Kiểm tra mạng rồi thử lại.', 'network');
}

/** Exchanges a Google ID token for a session. Rejects AuthError with a Vietnamese message. */
export async function signInWithCredential(credential: string): Promise<AuthUser> {
  await backend.init();
  try {
    const r = await backend.send<LoginResponse>('POST', '/auth/google', { credential }, { timeout: 20_000 });
    if (!r || typeof r.token !== 'string' || !r.token || !r.user || typeof r.user.id !== 'string' || !r.user.id) {
      throw new AuthError('Máy chủ trả về dữ liệu đăng nhập không hợp lệ.', 'network');
    }
    const u: AuthUser = { id: r.user.id, name: r.user.name ?? '', email: r.user.email ?? '', picture: r.user.picture ?? '' };
    setSession({ token: r.token, user: u, base: base(), expires: typeof r.expires === 'number' ? r.expires : 0 });
    emit('toast', { message: `Đã đăng nhập${u.name ? ' bằng tài khoản ' + u.name : ''}. Dữ liệu đọc sẽ được đồng bộ.`, kind: 'ok' });
    return u;
  } catch (e) {
    throw toAuthError(e);
  }
}

/** Android: native account picker, then the same exchange. */
export async function signInNative(): Promise<AuthUser> {
  const id = backend.auth?.clientId;
  if (!available() || !id) throw new AuthError('Máy chủ chưa bật đăng nhập Google.', 'unavailable');
  let token: string;
  try {
    token = await nativeGoogleIdToken(id);
  } catch (e) {
    throw toAuthError(e);
  }
  return signInWithCredential(token);
}

/** Revokes the session on the server (best effort), forgets it here and stops syncing. Local data stays. */
export async function signOut(): Promise<void> {
  if (signedIn()) {
    try {
      await backend.send('POST', '/auth/logout', {}, { timeout: 5_000 });
    } catch {
      /* offline or already revoked: the token is dropped locally anyway */
    }
  }
  setSession(null);
  try {
    window.google?.accounts.id.disableAutoSelect();
  } catch {
    /* script not loaded */
  }
  void nativeSignOut();
}

/** Checks the stored session with the server; 401 signs out (backend layer), other errors keep the session. */
export async function refresh(): Promise<void> {
  if (!signedIn()) return;
  try {
    const r = await backend.get<{ user?: Partial<AuthUser> }>('/auth/me', { timeout: 10_000 });
    const u = r.user;
    if (u && typeof u.id === 'string' && u.id === session()?.user.id) {
      updateUser({ id: u.id, name: u.name ?? '', email: u.email ?? '', picture: u.picture ?? '' });
    }
  } catch {
    /* offline: stay signed in */
  }
}

// ---------------------------------------------------------------- Google Identity Services (browser, desktop)

let gsi: Promise<GsiApi> | null = null;

/** Loads the Google script on first use (never at boot). */
export function loadGsi(): Promise<GsiApi> {
  if (window.google?.accounts?.id) return Promise.resolve(window.google);
  if (gsi) return gsi;
  gsi = new Promise<GsiApi>((resolve, reject) => {
    const s = document.createElement('script');
    s.src = GSI_SRC;
    s.async = true;
    s.defer = true;
    s.onload = () => (window.google?.accounts?.id ? resolve(window.google) : reject(new Error('gsi missing')));
    s.onerror = () => {
      s.remove();
      reject(new Error('gsi blocked'));
    };
    document.head.appendChild(s);
  }).catch(() => {
    gsi = null;
    throw new AuthError('Không tải được dịch vụ đăng nhập của Google. Kiểm tra mạng rồi thử lại.', 'network');
  });
  return gsi;
}

/**
 * Draws the official Google button into `host`. `onResult` gets the signed-in user, or the error to show.
 * Resolves when the button is on screen.
 */
export async function renderButton(host: HTMLElement, onResult: (r: { user: AuthUser } | { error: AuthError }) => void): Promise<void> {
  const id = backend.auth?.clientId;
  if (!available() || !id) throw new AuthError('Máy chủ chưa bật đăng nhập Google.', 'unavailable');
  const g = await loadGsi();
  g.accounts.id.initialize({
    client_id: id,
    auto_select: false,
    cancel_on_tap_outside: true,
    use_fedcm_for_prompt: true,
    callback: (resp: { credential?: string }) => {
      if (!resp.credential) return onResult({ error: new AuthError('Google không trả về thông tin đăng nhập.', 'bad_token') });
      signInWithCredential(resp.credential).then(
        (u) => onResult({ user: u }),
        (e: unknown) => onResult({ error: toAuthError(e) }),
      );
    },
  });
  host.textContent = '';
  g.accounts.id.renderButton(host, { type: 'standard', theme: 'outline', size: 'large', text: 'signin_with', shape: 'pill', locale: 'vi', logo_alignment: 'left', width: Math.min(320, Math.max(200, host.clientWidth || 280)) });
}

// ---------------------------------------------------------------- state events

const changes = new Emitter<void>();
/** Subscribes to anything the account UI shows: session changes and the backend (sign-in availability). */
export const onChange = (fn: () => void): (() => void) => {
  const offs = [on('auth', fn), on('backend', fn), changes.on(fn)];
  return () => offs.forEach((o) => o());
};

let started = false;
/** Called once by main.ts after the backend is chosen: validates the stored session. */
export async function init(): Promise<void> {
  if (!started) {
    started = true;
    on('backend', () => void refresh());
  }
  await backend.init();
  await refresh();
  changes.emit();
}

export const auth = { init, available, signedIn, user, mode, signInWithCredential, signInNative, signOut, refresh, renderButton, loadGsi, onChange, accountId: (): string => accountId(base()) };
