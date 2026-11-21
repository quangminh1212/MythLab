/**
 * The GitHub token at rest. The token is encrypted with AES-GCM using a NON-EXTRACTABLE CryptoKey that is generated
 * once and kept in IndexedDB (`mythlab` / `secrets`), so the localStorage value (and any copy of it: browser profile
 * dumps, sync, screenshots of devtools) holds only `{v:1, iv, ct}` in base64 and the key bytes can never be read back
 * by script.
 *
 * What this protects: casual extraction of localStorage. What it does NOT protect: script running in this origin
 * (XSS can call `getToken()` or decrypt through the same key), a rooted/unlocked device, or a memory dump.
 *
 * Sync call sites read the in-memory cache (`peekToken()`), filled by `initSecret()` during boot. Writes update the
 * cache at once and persist in order; a failure to encrypt (no `crypto.subtle` on an insecure http origin, no
 * IndexedDB in private mode) falls back to the previous plaintext storage and `isProtected()` turns false.
 * The localStorage key name is frozen: `mythlab.ghToken`.
 */
import { idb, store } from './store';

export const TOKEN_KEY = 'mythlab.ghToken';
const KEY_ID = 'token-key-v1';
const AAD = new TextEncoder().encode(TOKEN_KEY);

interface Sealed {
  v: 1;
  iv: string;
  ct: string;
}

let cache = '';
let prot = false;
let ready: Promise<void> | null = null;
let chain: Promise<void> = Promise.resolve();
let listening = false;
let latest = '';
let gen = 0; // bumped by every setToken so a queued load() never overwrites a newer value

const canCrypto = (): boolean => {
  try {
    return typeof crypto !== 'undefined' && !!crypto.subtle && typeof indexedDB !== 'undefined';
  } catch {
    return false;
  }
};

function b64(buf: ArrayBuffer | Uint8Array): string {
  const u = buf instanceof Uint8Array ? buf : new Uint8Array(buf);
  let s = '';
  for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode(...u.subarray(i, i + 0x8000));
  return btoa(s);
}
function unb64(s: string): Uint8Array<ArrayBuffer> {
  const bin = atob(s);
  const u = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return u;
}

const isSealed = (v: unknown): v is Sealed => {
  const o = v as Partial<Sealed> | null;
  return !!o && typeof o === 'object' && o.v === 1 && typeof o.iv === 'string' && typeof o.ct === 'string';
};

/** The stored key, or a new one (created with add-if-absent so two tabs end up with the same key); null when unavailable. */
async function getKey(create: boolean): Promise<CryptoKey | null> {
  if (!canCrypto()) return null;
  try {
    let k = await idb.secretGet<CryptoKey>(KEY_ID);
    if (k || !create) return k ?? null;
    const fresh = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
    await idb.secretAdd(KEY_ID, fresh);
    k = await idb.secretGet<CryptoKey>(KEY_ID); // whoever won the race
    return k ?? null;
  } catch {
    return null;
  }
}

async function seal(plain: string): Promise<Sealed | null> {
  const key = await getKey(true);
  if (!key) return null;
  try {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv, additionalData: AAD }, key, new TextEncoder().encode(plain));
    return { v: 1, iv: b64(iv), ct: b64(ct) };
  } catch {
    return null;
  }
}

/** Plaintext of a sealed value, or null when the key is gone or the data was altered or is corrupted. */
async function open(s: Sealed): Promise<string | null> {
  const key = await getKey(false);
  if (!key) return null;
  try {
    const pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: unb64(s.iv), additionalData: AAD }, key, unb64(s.ct));
    return new TextDecoder().decode(pt);
  } catch {
    return null;
  }
}

/** Persists `token` (encrypted when possible; plaintext as the documented fallback). */
async function persist(token: string): Promise<void> {
  const sealed = await seal(token);
  if (sealed) {
    prot = true;
    store.set(TOKEN_KEY, sealed);
  } else {
    prot = false;
    store.set(TOKEN_KEY, token);
  }
}

async function load(): Promise<void> {
  const g = gen;
  await loadInner();
  if (g !== gen) cache = latest;
}

async function loadInner(): Promise<void> {
  prot = canCrypto();
  const raw = store.get<unknown>(TOKEN_KEY, '');
  if (isSealed(raw)) {
    const t = await open(raw);
    if (t == null) {
      // unreadable (key lost, data corrupted, or IndexedDB briefly unavailable): keep the blob, it may open on a later
      // boot, and the user is asked for the token meanwhile. The next save overwrites it.
      cache = '';
    } else {
      cache = t;
      prot = true;
    }
  } else if (typeof raw === 'string' && raw) {
    cache = raw;
    await persist(raw); // legacy plaintext: encrypt and rewrite (stays plaintext only when encryption is impossible)
  } else {
    cache = ''; // empty or an unknown (maybe newer) shape: leave it untouched
  }
}

function queue(fn: () => Promise<void>): Promise<void> {
  chain = chain.then(fn, fn).catch(() => undefined);
  return chain;
}

/** Loads the token into memory (decrypting it, migrating legacy plaintext). Idempotent; call once during boot. */
export function initSecret(): Promise<void> {
  if (!ready) ready = queue(load);
  if (!listening && typeof window !== 'undefined') {
    listening = true;
    // another tab saved or forgot the token
    window.addEventListener('storage', (e) => {
      if (e.key === null || e.key === TOKEN_KEY) void queue(load);
    });
  }
  return ready;
}

/** Synchronous read of the in-memory copy ('' before `initSecret()` resolved or when there is no token). */
export const peekToken = (): string => cache;

export async function getToken(): Promise<string> {
  await initSecret();
  await chain;
  return cache;
}

/** Saves the token. The cache changes immediately; the promise resolves once it is written. Empty text forgets it. */
export function setToken(token: string): Promise<void> {
  const t = String(token || '');
  cache = t;
  latest = t;
  gen++;
  if (!ready) ready = Promise.resolve();
  return queue(async () => {
    if (!t) store.del(TOKEN_KEY);
    else await persist(t);
  });
}

export const clearToken = (): Promise<void> => setToken('');

/** Resolves when every pending write reached storage. */
export const flushToken = (): Promise<void> => chain;

/** True when the token is (or would be) stored encrypted on this device. */
export const isProtected = (): boolean => prot;

/** Vietnamese hint for the settings screen. */
export const protectionHint = (): string =>
  prot ? 'Token được mã hóa trên thiết bị này.' : 'Trình duyệt này không hỗ trợ mã hóa, token lưu dạng thường.';

/** Test hook: forget the in-memory state (a "reload" of this module without re-importing it). */
export function _resetSecret(): void {
  cache = '';
  latest = '';
  gen = 0;
  prot = false;
  ready = null;
  chain = Promise.resolve();
}
