/* Piper on-device synthesis worker (classic worker, loaded only after the user picked Piper).
 * Messages in:  {t:'init', id, base, model:ArrayBuffer, config:object}  |  {t:'synth', id, text, sid}
 * Messages out: {id, ok:true}  |  {id, pcm:Float32Array, rate}  |  {id, err}
 * Runtime files next to this script (copied by scripts/copy-tts.mjs):
 *   ort/ort.wasm.min.mjs, ort/ort-wasm-simd-threaded.{mjs,wasm}   onnxruntime-web, single thread
 *   piper/piper_phonemize.{js,wasm,data}                          espeak-ng "vi" -> phoneme ids
 */
'use strict';

var ort = null;
var session = null;
var cfg = null;
var phon = null; // { wasm: ArrayBuffer, data: ArrayBuffer }
var chain = Promise.resolve();

function bytes(url) {
  return fetch(url).then(function (r) {
    if (!r.ok) throw new Error('Không tải được ' + url + ' (' + r.status + ')');
    return r.arrayBuffer();
  });
}

async function runtime(base) {
  if (!ort) {
    ort = await import(base + 'ort/ort.wasm.min.mjs');
    ort.env.wasm.wasmPaths = base + 'ort/';
    ort.env.wasm.numThreads = 1;
    ort.env.wasm.proxy = false;
  }
  if (!phon) {
    importScripts(base + 'piper/piper_phonemize.js');
    var got = await Promise.all([bytes(base + 'piper/piper_phonemize.wasm'), bytes(base + 'piper/piper_phonemize.data')]);
    phon = { wasm: got[0], data: got[1] };
  }
}

async function init(m) {
  await runtime(m.base);
  if (session) {
    try {
      await session.release();
    } catch (e) {
      /* already gone */
    }
    session = null;
  }
  cfg = m.config;
  session = await ort.InferenceSession.create(new Uint8Array(m.model), { executionProviders: ['wasm'], graphOptimizationLevel: 'all' });
}

/** espeak-ng -> phoneme ids of the voice (the module is instantiated per call, like the reference wrapper). */
function phonemize(text) {
  return new Promise(function (resolve, reject) {
    var done = false;
    createPiperPhonemize({
      print: function (line) {
        if (done) return;
        try {
          var ids = JSON.parse(line).phoneme_ids;
          done = true;
          resolve(ids);
        } catch (e) {
          /* not a result line */
        }
      },
      printErr: function () {},
      wasmBinary: phon.wasm,
      getPreloadedPackage: function () {
        return phon.data;
      },
      locateFile: function (f) {
        return f;
      },
    })
      .then(function (mod) {
        try {
          mod.callMain(['-l', 'vi', '--input', JSON.stringify([{ text: text }]), '--espeak_data', '/espeak-ng-data']);
        } catch (e) {
          /* callMain may throw ExitStatus */
        }
        if (!done) reject(new Error('Không tách được âm tiết'));
      })
      .catch(reject);
  });
}

/** Some voices (vivos, 25hours) were trained on a smaller symbol set (130, no tone digits) than espeak's ids (up to 142);
 * an id past the model's embedding table makes onnxruntime fail, so keep only ids the voice knows (same numbering as
 * the full map) and rebuild the pad (0) between them: ^ 0 p 0 p ... 0 $ . */
function supported(ids) {
  var map = cfg && cfg.phoneme_id_map;
  if (!ids || !map) return ids;
  var ok = {};
  Object.keys(map).forEach(function (k) {
    // Piper configs list ids as arrays ([3]); phoonnx configs (Vais1000 int8) as plain numbers (3)
    [].concat(map[k] == null ? [] : map[k]).forEach(function (id) { ok[id] = true; });
  });
  var toks = ids.filter(function (x) { return x !== 0 && ok[x]; });
  var out = [];
  for (var i = 0; i < toks.length; i++) {
    out.push(toks[i]);
    if (toks[i] !== 2 && i < toks.length - 1) out.push(0);
  }
  return out;
}

async function synth(m) {
  if (!session) throw new Error('Giọng Piper chưa nạp');
  var ids = supported(await phonemize(m.text));
  if (!ids || !ids.length) return { pcm: new Float32Array(0), rate: cfg.audio.sample_rate };
  var inf = cfg.inference || {};
  var feeds = {
    input: new ort.Tensor('int64', BigInt64Array.from(ids, function (x) { return BigInt(x); }), [1, ids.length]),
    input_lengths: new ort.Tensor('int64', BigInt64Array.from([BigInt(ids.length)]), [1]),
    scales: new ort.Tensor('float32', Float32Array.from([inf.noise_scale == null ? 0.667 : inf.noise_scale, inf.length_scale == null ? 1 : inf.length_scale, inf.noise_w == null ? 0.8 : inf.noise_w]), [3]),
  };
  // multi-speaker models take the speaker as int64[1]; single-speaker ones have no such input
  if (session.inputNames.indexOf('sid') >= 0) {
    var n = cfg.num_speakers || 1;
    var sid = Number(m.sid) | 0;
    feeds.sid = new ort.Tensor('int64', BigInt64Array.from([BigInt(sid >= 0 && sid < n ? sid : 0)]), [1]);
  }
  var out = await session.run(feeds);
  var data = out.output.data;
  return { pcm: data, rate: cfg.audio.sample_rate };
}

self.onmessage = function (e) {
  var m = e.data;
  chain = chain.then(async function () {
    try {
      if (m.t === 'init') {
        await init(m);
        self.postMessage({ id: m.id, ok: true });
      } else if (m.t === 'synth') {
        var r = await synth(m);
        self.postMessage({ id: m.id, pcm: r.pcm, rate: r.rate }, [r.pcm.buffer]);
      }
    } catch (err) {
      self.postMessage({ id: m.id, err: String((err && err.message) || err) });
    }
  });
};
