import { afterEach, describe, expect, it, vi } from 'vitest';

vi.mock('./piper', async (orig) => ({ ...(await orig<typeof import('./piper')>()), piperSupported: () => true, piperInstalled: () => false }));
vi.mock('./autovoice', () => ({ installVoiceOnce: vi.fn() }));
vi.mock('../core/ui', () => ({ toast: vi.fn(), confirmDialog: vi.fn(async () => false) }));

interface Call {
  text: string;
  queueStrategy?: number;
  done(): void;
}

async function setup() {
  vi.resetModules();
  const { S } = await import('../core/settings');
  S.engine = 'native';
  const calls: Call[] = [];
  const stop = vi.fn(async () => {});
  vi.stubGlobal('Capacitor', {
    Plugins: {
      TextToSpeech: {
        getSupportedVoices: async () => ({ voices: [{ voiceURI: 'vn', lang: 'vi-VN' }] }),
        speak: (o: { text: string; queueStrategy?: number }) => new Promise<void>((res) => calls.push({ text: o.text, ...(o.queueStrategy !== undefined ? { queueStrategy: o.queueStrategy } : {}), done: res })),
        stop,
      },
    },
  });
  const e = await import('./engines');
  await e.settleEngine();
  return { e, calls, stop };
}

const chunk = (...t: string[]) => {
  let at = 0;
  const sents = t.map((x) => {
    const s = { s: at, e: at + x.length, at, len: x.length };
    at += x.length + 1;
    return s;
  });
  return { p: 0, text: t.join(' '), sents };
};
const tick = () => new Promise((r) => setTimeout(r, 0));

afterEach(() => vi.unstubAllGlobals());

describe('native engine queues utterances in the speech service', () => {
  it('queues every sentence of a chunk at once (flush first, then add) and reports sentences as they finish', async () => {
    const { e, calls } = await setup();
    const sent: number[] = [];
    const c = chunk('Câu một.', 'Câu hai.', 'Câu ba.');
    const p = e.speak('native', c, { from: 0, rate: 1, pitch: 1, onSent: (k) => sent.push(k) });
    await tick();
    expect(calls.map((x) => x.queueStrategy)).toEqual([0, 1, 1]);
    expect(sent).toEqual([0]);
    calls[0]!.done();
    await tick();
    expect(sent).toEqual([0, 1]);
    calls[1]!.done();
    calls[2]!.done();
    await p;
    expect(sent).toEqual([0, 1, 2]);
  });

  it('queues the announced next chunk behind the current one and adopts it without flushing', async () => {
    const { e, calls, stop } = await setup();
    const a = chunk('A một.', 'A hai.');
    const b = chunk('B một.');
    e.prefetch('native', b);
    const pa = e.speak('native', a, { from: 0, rate: 1, pitch: 1, onSent() {} });
    await tick();
    expect(calls.map((x) => x.text)).toEqual(['A một.', 'A hai.', 'B một.']);
    expect(calls.map((x) => x.queueStrategy)).toEqual([0, 1, 1]);
    calls[0]!.done();
    calls[1]!.done();
    await pa;
    // the player now asks for chunk b: nothing new is sent, the queue is followed
    const sent: number[] = [];
    const pb = e.speak('native', b, { from: 0, rate: 1, pitch: 1, onSent: (k) => sent.push(k) });
    await tick();
    expect(calls).toHaveLength(3);
    expect(stop).not.toHaveBeenCalled();
    expect(sent).toEqual([0]);
    calls[2]!.done();
    await pb;
  });

  it('a changed speed does not adopt the queue: it is flushed and spoken again', async () => {
    const { e, calls, stop } = await setup();
    const a = chunk('A một.');
    const b = chunk('B một.');
    e.prefetch('native', b);
    const pa = e.speak('native', a, { from: 0, rate: 1, pitch: 1, onSent() {} });
    await tick();
    calls[0]!.done();
    await pa;
    void e.speak('native', b, { from: 0, rate: 1.5, pitch: 1, onSent() {} }).catch(() => {});
    await tick();
    expect(stop).toHaveBeenCalled();
    expect(calls.at(-1)).toMatchObject({ text: 'B một.', queueStrategy: 0 });
  });

  it('stopAll drops the queue and rejects the pending chunk as stopped', async () => {
    const { e, calls, stop } = await setup();
    const p = e.speak('native', chunk('A một.'), { from: 0, rate: 1, pitch: 1, onSent() {} });
    await tick();
    expect(calls).toHaveLength(1);
    e.stopAll();
    expect(stop).toHaveBeenCalledOnce();
    await expect(p).rejects.toBeInstanceOf(e.Stopped);
  });
});
