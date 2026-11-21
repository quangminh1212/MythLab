import { describe, expect, it } from 'vitest';
import { Lru } from './lru';

describe('Lru', () => {
  it('evicts the least recently used key when over the cap', () => {
    const l = new Lru(3);
    expect(l.add('a')).toEqual([]);
    l.add('b');
    l.add('c');
    l.touch('a');
    expect(l.add('d')).toEqual(['b']);
    expect(l.keys()).toEqual(['c', 'a', 'd']);
  });

  it('ignores a touch of an unknown key and does not mark it dirty', () => {
    const l = new Lru(2);
    l.touch('zzz');
    expect(l.dirty).toBe(false);
    expect(l.size).toBe(0);
  });

  it('round-trips through JSON and keeps the order', () => {
    const l = new Lru(5);
    ['a', 'b', 'c'].forEach((k) => l.add(k));
    l.touch('a');
    const copy = new Lru(5, JSON.parse(JSON.stringify(l.toJSON())));
    expect(copy.keys()).toEqual(['b', 'c', 'a']);
    copy.add('d');
    expect(copy.keys().at(-1)).toBe('d');
  });

  it('survives corrupt saved state', () => {
    expect(new Lru(2, { u: [['a', 'x'], 5, ['b', 1]], c: 'no' }).keys()).toEqual(['b']);
    expect(new Lru(2, 'garbage').size).toBe(0);
    expect(new Lru(0).max).toBe(1);
  });

  it('sync drops missing keys, adopts unknown ones as oldest and evicts over the cap', () => {
    const l = new Lru(3);
    l.add('x');
    l.add('y');
    const out = l.sync(['old1', 'y', 'old2', 'old3']);
    expect(l.has('x')).toBe(false);
    expect(out).toEqual(['old1']);
    expect(l.keys()).toEqual(['old2', 'old3', 'y']);
  });

  it('delete and clear update the index', () => {
    const l = new Lru(3);
    l.add('a');
    l.add('b');
    l.delete('a');
    expect(l.keys()).toEqual(['b']);
    l.clear();
    expect(l.size).toBe(0);
  });
});
