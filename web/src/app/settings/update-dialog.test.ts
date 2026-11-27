import { describe, expect, it } from 'vitest';
import { dialogView } from './update-dialog';

const latest = { versionCode: 2, versionName: '1.2.0', url: 'https://x/a.apk', sha256: 'a'.repeat(64), size: 5 << 20, notes: 'Sửa lỗi' };
const current = { versionCode: 1, versionName: '1.1.0', canInstall: true };

describe('dialogView', () => {
  it('offers the install with size and notes', () => {
    const v = dialogView({ kind: 'available', current, latest });
    expect(v.title).toBe('Có bản mới 1.2.0');
    expect(String(v.body)).toContain('Sửa lỗi');
    expect(String(v.footer)).toContain('data-up="start"');
  });
  it('shows download progress', () => {
    const v = dialogView({ kind: 'downloading', latest, loaded: 1 << 20, total: 4 << 20 });
    expect(String(v.body)).toContain('25%');
  });
});
