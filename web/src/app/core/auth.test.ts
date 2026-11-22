import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError } from './backend/types';

const be = vi.hoisted(() => ({
  kind: 'server' as string,
  serverBase: 'http://srv' as string | null,
  auth: { google: true, clientId: 'cid' } as { google: boolean; clientId: string } | null,
  features: ['progress', 'auth', 'library'],
  get: vi.fn(),
  send: vi.fn(),
  init: vi.fn(async () => 'server'),
}));
vi.mock('./backend', () => ({ backend: be }));

import { auth, AuthError } from './auth';
import { session, setSession, _resetAuth } from './auth-token';

beforeEach(() => {
  localStorage.clear();
  _resetAuth();
  be.kind = 'server';
  be.auth = { google: true, clientId: 'cid' };
  be.get.mockReset();
  be.send.mockReset();
});

const login = { token: 'T1', expires: 1, user: { id: 'u1', name: 'An', email: 'an@x.vn', picture: 'https://lh3.googleusercontent.com/a' } };

describe('auth', () => {
  it('is available only with a server that advertises google', () => {
    expect(auth.available()).toBe(true);
    be.auth = null;
    expect(auth.available()).toBe(false);
    be.auth = { google: true, clientId: 'cid' };
    be.kind = 'github';
    expect(auth.available()).toBe(false);
  });

  it('exchanges a Google credential for a stored session', async () => {
    be.send.mockResolvedValue(login);
    const u = await auth.signInWithCredential('ID-TOKEN');
    expect(be.send).toHaveBeenCalledWith('POST', '/auth/google', { credential: 'ID-TOKEN' }, expect.anything());
    expect(u.email).toBe('an@x.vn');
    expect(auth.signedIn()).toBe(true);
    expect(session()).toMatchObject({ token: 'T1', base: 'http://srv' });
    expect(auth.accountId()).toBe('u1');
  });

  it('maps server refusals to Vietnamese messages and stays signed out', async () => {
    be.send.mockRejectedValue(new ApiError('x', 403, { code: 'not_allowed' }));
    await expect(auth.signInWithCredential('a')).rejects.toMatchObject({ code: 'not_allowed' });
    be.send.mockRejectedValue(new ApiError('x', 401, { code: 'bad_token' }));
    await expect(auth.signInWithCredential('a')).rejects.toBeInstanceOf(AuthError);
    be.send.mockResolvedValue({ token: '', user: {} });
    await expect(auth.signInWithCredential('a')).rejects.toBeInstanceOf(AuthError);
    expect(auth.signedIn()).toBe(false);
  });

  it('signOut revokes on the server, drops the token and keeps local data', async () => {
    localStorage.setItem('mythlab.bookmarks', '[{"id":"b"}]');
    setSession({ token: 'T1', user: login.user, base: 'http://srv', expires: 0 });
    be.send.mockResolvedValue({});
    await auth.signOut();
    expect(be.send).toHaveBeenCalledWith('POST', '/auth/logout', {}, expect.anything());
    expect(auth.signedIn()).toBe(false);
    expect(localStorage.getItem('mythlab.auth')).toBeNull();
    expect(localStorage.getItem('mythlab.bookmarks')).not.toBeNull();
  });

  it('signOut works offline', async () => {
    setSession({ token: 'T1', user: login.user, base: 'http://srv', expires: 0 });
    be.send.mockRejectedValue(new ApiError('net', 0, { code: 'network' }));
    await auth.signOut();
    expect(auth.signedIn()).toBe(false);
  });

  it('a session issued by another server does not count as signed in', () => {
    setSession({ token: 'T1', user: login.user, base: 'http://other', expires: 0 });
    expect(auth.signedIn()).toBe(false);
    expect(auth.accountId()).toBe('');
  });

  it('refresh keeps the session on network errors and updates the profile', async () => {
    setSession({ token: 'T1', user: login.user, base: 'http://srv', expires: 0 });
    be.get.mockRejectedValueOnce(new ApiError('net', 0, { code: 'network' }));
    await auth.refresh();
    expect(auth.signedIn()).toBe(true);
    be.get.mockResolvedValueOnce({ user: { ...login.user, name: 'An B' } });
    await auth.refresh();
    expect(auth.user()?.name).toBe('An B');
  });
});
