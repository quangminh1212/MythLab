import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AUTH_KEY, authHeader, authToken, session, setSession, _resetAuth } from '../auth-token';
import { on } from '../events';
import { createServerBackend } from './server';

const user = { id: 'sub1', name: 'An', email: 'an@example.com', picture: '' };
const sign = (base = 'http://srv'): void => setSession({ token: 'TOK', user, base, expires: 0 });

let calls: { url: string; headers: Record<string, string>; method: string }[];
function fetchStub(status = 200, body: unknown = { entries: [], now: 1 }): void {
  calls = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init: RequestInit = {}) => {
      calls.push({ url, headers: { ...((init.headers as Record<string, string>) ?? {}) }, method: init.method ?? 'GET' });
      return new Response(status === 204 ? null : JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
    }),
  );
}

beforeEach(() => {
  localStorage.clear();
  _resetAuth();
});
afterEach(() => vi.unstubAllGlobals());

describe('session state', () => {
  it('persists under mythlab.auth, is scoped to the issuing server and emits auth', () => {
    const seen: boolean[] = [];
    const off = on('auth', (e) => seen.push(e.signedIn));
    sign();
    expect(JSON.parse(localStorage.getItem(AUTH_KEY) as string)).toMatchObject({ token: 'TOK', base: 'http://srv' });
    expect(authToken('http://srv')).toBe('TOK');
    expect(authToken('http://other')).toBe('');
    expect(authHeader('http://srv')).toEqual({ Authorization: 'Bearer TOK' });
    expect(authHeader('http://other')).toEqual({});
    _resetAuth();
    expect(session()?.user.id).toBe('sub1');
    setSession(null);
    expect(localStorage.getItem(AUTH_KEY)).toBeNull();
    expect(seen).toEqual([true, false]);
    off();
  });

  it('ignores a corrupt stored session', () => {
    localStorage.setItem(AUTH_KEY, JSON.stringify({ token: 5 }));
    _resetAuth();
    expect(session()).toBeNull();
  });
});

describe('Bearer on the server backend', () => {
  it('goes only to the routes that take it', async () => {
    sign();
    fetchStub();
    const b = createServerBackend('http://srv', 'LANKEY');
    await b.get('/progress?since=0');
    await b.get('/library?since=0');
    await b.get('/auth/me');
    await b.get('/sources');
    await b.send('PUT', '/library', { entries: [] });
    await b.send('POST', '/auth/google', { credential: 'x' });
    const got = calls.map((c) => [c.url.replace('http://srv/api', ''), c.headers.Authorization ?? null]);
    expect(got).toEqual([
      ['/progress?since=0', 'Bearer TOK'],
      ['/library?since=0', 'Bearer TOK'],
      ['/auth/me', 'Bearer TOK'],
      ['/sources', null],
      ['/library', 'Bearer TOK'],
      ['/auth/google', null],
    ]);
    expect(calls[0]?.headers['X-MythLab-Key']).toBe('LANKEY');
  });

  it('is never sent to another server', async () => {
    sign('http://srv');
    fetchStub();
    await createServerBackend('http://elsewhere').get('/progress?since=0');
    expect(calls[0]?.headers.Authorization).toBeUndefined();
  });

  it('a 401 on a Bearer request signs this device out with a toast', async () => {
    sign();
    fetchStub(401, { error: 'unauthorized' });
    const toasts: string[] = [];
    const off = on('toast', (t) => toasts.push(t.message));
    await expect(createServerBackend('http://srv').get('/progress?since=0')).rejects.toMatchObject({ status: 401 });
    expect(session()).toBeNull();
    expect(toasts.join(' ')).toMatch(/hết hạn/);
    off();
  });

  it('a 401 without a session (wrong access key) changes nothing', async () => {
    fetchStub(401, { error: 'unauthorized' });
    const toasts: string[] = [];
    const off = on('toast', (t) => toasts.push(t.message));
    await expect(createServerBackend('http://srv').get('/progress?since=0')).rejects.toMatchObject({ status: 401 });
    expect(toasts).toEqual([]);
    off();
  });

  it('accepts 204 (logout) and reads the ping auth block', async () => {
    sign();
    fetchStub(204);
    await expect(createServerBackend('http://srv').send('POST', '/auth/logout', {})).resolves.toEqual({});
    fetchStub(200, { ok: true, app: 'mythlab', api: 2, features: ['progress', 'auth', 'library'], auth: { google: true, client_id: 'cid.apps.googleusercontent.com' } });
    const b = createServerBackend('http://srv');
    await b.ping();
    expect(b.auth).toEqual({ google: true, clientId: 'cid.apps.googleusercontent.com' });
    expect(b.features).toContain('library');
    fetchStub(200, { ok: true, app: 'mythlab', api: 2 });
    await b.ping();
    expect(b.auth).toBeNull();
  });
});
