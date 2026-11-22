/**
 * The Google session of this device: opaque session token + profile, stored under `mythlab.auth`.
 * Kept free of network code so the backend layer can read the token without importing `auth.ts` (which imports the
 * backend). The token is a bearer secret: it is sent only to the server that issued it, only on the routes that take
 * it, and is never part of the settings backup.
 */
import { emit } from './events';
import { store } from './store';

export const AUTH_KEY = 'mythlab.auth';

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  picture: string;
}
export interface Session {
  token: string;
  user: AuthUser;
  /** Server base the token was issued by ('' = same origin). */
  base: string;
  /** Expiry reported by the server (ms), 0 when unknown. */
  expires: number;
}

let cache: Session | null | undefined;

function clean(raw: unknown): Session | null {
  const r = raw as Partial<Session> | null;
  if (!r || typeof r !== 'object' || typeof r.token !== 'string' || !r.token) return null;
  const u = (r.user ?? {}) as Partial<AuthUser>;
  if (typeof u.id !== 'string' || !u.id) return null;
  return {
    token: r.token,
    user: { id: u.id, name: typeof u.name === 'string' ? u.name : '', email: typeof u.email === 'string' ? u.email : '', picture: typeof u.picture === 'string' ? u.picture : '' },
    base: typeof r.base === 'string' ? r.base : '',
    expires: typeof r.expires === 'number' && Number.isFinite(r.expires) ? r.expires : 0,
  };
}

export function session(): Session | null {
  if (cache === undefined) cache = clean(store.get<unknown>(AUTH_KEY, null));
  return cache;
}

/** The token to send to the server at `base` ('' when signed out or when the token belongs to another server). */
export function authToken(base?: string): string {
  const s = session();
  if (!s) return '';
  if (base !== undefined && s.base !== base) return '';
  return s.token;
}

/** Headers for a request to the configured server (empty when signed out). */
export function authHeader(base?: string): Record<string, string> {
  const t = authToken(base);
  return t ? { Authorization: 'Bearer ' + t } : {};
}

/** Id of the signed-in Google account ('' when signed out): keys the per-account sync state. */
export function accountId(base?: string): string {
  const s = session();
  return s && (base === undefined || s.base === base) ? s.user.id : '';
}

export function setSession(next: Session | null): void {
  const was = session();
  cache = next;
  if (next) store.set(AUTH_KEY, next);
  else store.del(AUTH_KEY);
  if (!!was !== !!next || was?.user.id !== next?.user.id || was?.token !== next?.token) emit('auth', { signedIn: !!next });
}

/** Updates the profile (picture, name) of the current session without changing the token. */
export function updateUser(user: AuthUser): void {
  const s = session();
  if (!s) return;
  cache = { ...s, user };
  store.set(AUTH_KEY, cache);
  emit('auth', { signedIn: true });
}

/** The server refused `token` (401): it is revoked or expired, so this device is signed out. */
export function rejectToken(token: string): void {
  if (!token || session()?.token !== token) return;
  setSession(null);
  emit('toast', { message: 'Phiên đăng nhập hết hạn. Hãy đăng nhập lại.', kind: 'error' });
}

/** Test hook. */
export function _resetAuth(): void {
  cache = undefined;
}
