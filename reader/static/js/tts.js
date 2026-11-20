// ML.tts — bộ đọc native (Capacitor), browser (Web Speech); edge vẫn nằm trong app.js
window.ML = window.ML || {};
(() => {
  const S = () => window.ML.settings?.S || {};
  const toast = (m, ms) => window.ML.toast?.(m, ms);
  const plug = (n) => window.Capacitor?.Plugins?.[n];
  const isVi = (lang) => /^vi/i.test(lang || "");
  const hasBrowser = () => "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
  const abortErr = () => Object.assign(new Error("stopped"), { name: "AbortError" });

  // ---- làm sạch văn bản trước khi đọc
  const BAD = /[^\p{L}\p{M}\p{N}\s.,!?…:;"'“”‘’()\-–—]/gu;
  function clean(text) {
    let t = String(text ?? "");
    if (S().ttsClean === false) return t;
    t = t.replace(BAD, " ")
      .replace(/\.{3,}/g, "…").replace(/([!?…,;:])\1+/g, "$1").replace(/([-–—])\1+/g, "$1")
      .replace(/\(\s*\)|“\s*”|"\s*"/g, " ")
      .replace(/\s+([.,!?…:;])/g, "$1").replace(/\s+/g, " ").trim();
    return /[\p{L}\p{N}]/u.test(t) ? t : "";
  }
  // tách đoạn dài thành các mẩu <= max theo dấu câu
  function split(text, max) {
    if (text.length <= max) return [text];
    const parts = (text.match(/[^.!?…,;:]+[.!?…,;:]*\s*/gu) || [text]).reduce((a, s) => {
      if (a.length && (a[a.length - 1] + s).length <= max) a[a.length - 1] += s; else a.push(s); return a; }, []);
    return parts.flatMap((p) => { const o = []; for (let k = 0; k < p.length; k += max) o.push(p.slice(k, k + max)); return o; })
      .map((p) => p.trim()).filter(Boolean);
  }

  function engines() {
    const out = [];
    if (window.ML.backend?.kind === "server") out.push("edge");
    if (hasBrowser()) out.push("browser");
    if (window.Capacitor && plug("TextToSpeech")) out.push("native");
    return out;
  }

  // ---- danh sách giọng
  let nativeList = null, warnedVi = false;
  async function nativeVoices() {
    const p = plug("TextToSpeech");
    if (!p) return [];
    if (!nativeList) {
      const r = await p.getSupportedVoices().catch(() => ({ voices: [] }));
      nativeList = r?.voices || [];
    }
    return nativeList;
  }
  function warnNoVi() {
    if (warnedVi) return;
    warnedVi = true;
    toast("Máy chưa có giọng tiếng Việt — cài “Speech Services by Google” rồi tải gói Tiếng Việt", 6000);
  }
  function browserVoices() {
    if (!hasBrowser()) return Promise.resolve([]);
    const now = speechSynthesis.getVoices();
    if (now.length) return Promise.resolve(now);
    return new Promise((res) => {
      const done = () => { speechSynthesis.removeEventListener?.("voiceschanged", done); res(speechSynthesis.getVoices()); };
      speechSynthesis.addEventListener?.("voiceschanged", done);
      setTimeout(done, 1500);
    });
  }
  const sortVi = (a, b) => isVi(b.lang) - isVi(a.lang);
  async function voices(engine) {
    if (engine === "edge") {
      const j = await window.ML.backend?.get("/voices").catch(() => null);
      return (j?.voices || []).map((v) => ({ id: v.id, lang: v.id.split("-").slice(0, 2).join("-"),
        name: String(v.name || v.id).replace(/^Microsoft\s+/, "").replace(/ Online \(Natural\)/, "") }));
    }
    if (engine === "native") {
      const vs = await nativeVoices();
      if (plug("TextToSpeech") && !vs.some((v) => isVi(v.lang))) warnNoVi();
      return vs.map((v) => ({ id: v.voiceURI, name: v.name || v.voiceURI, lang: v.lang })).sort(sortVi);
    }
    if (engine === "browser") {
      const vs = await browserVoices();
      return vs.map((v) => ({ id: v.voiceURI, name: v.name, lang: v.lang })).sort(sortVi);
    }
    return [];
  }

  // ---- phát
  let cur = null; // {reject, timer}
  function settle() { if (cur) { clearInterval(cur.timer); cur = null; } }

  async function speakNative(text, o, my) {
    const p = plug("TextToSpeech");
    if (!p) throw new Error("Không có bộ đọc của máy");
    const vs = await nativeVoices();
    let idx = vs.findIndex((v) => v.voiceURI === (o.voice || S().nativeVoice));
    if (idx < 0) {
      if (!vs.some((v) => isVi(v.lang)) && vs.length) warnNoVi();
      idx = undefined;
    }
    for (const piece of split(text, 3500)) {
      if (cur !== my) throw abortErr();
      try {
        await p.speak({ text: piece, lang: "vi-VN", rate: o.rate ?? 1, pitch: o.pitch ?? 1, volume: 1, category: "playback", voice: idx });
      } catch (e) {
        if (cur !== my) throw abortErr();
        if (/language/i.test(e?.message || "")) warnNoVi();
        throw e;
      }
    }
  }

  async function speakBrowser(text, o, my) {
    if (!hasBrowser()) throw new Error("Trình duyệt không hỗ trợ đọc");
    speechSynthesis.cancel();
    const vs = await browserVoices();
    if (cur !== my) throw abortErr();
    const want = o.voice || S().browserVoice;
    const voice = vs.find((v) => v.voiceURI === want) || vs.find((v) => isVi(v.lang) && /natural|online/i.test(v.name))
      || vs.find((v) => isVi(v.lang)) || null;
    // Chrome desktop tự ngắt giọng online sau ~15s: pause/resume định kỳ (Android thì pause = huỷ, nên bỏ qua)
    if (voice && !voice.localService && !/Android/i.test(navigator.userAgent))
      my.timer = setInterval(() => { if (speechSynthesis.speaking && !speechSynthesis.paused) { speechSynthesis.pause(); speechSynthesis.resume(); } }, 10000);
    const keep = []; // giữ tham chiếu để Chrome không GC utterance (mất onend)
    await new Promise((res, rej) => {
      const pieces = split(text, 230);
      pieces.forEach((piece, k) => {
        const u = new SpeechSynthesisUtterance(piece);
        u.lang = voice?.lang || "vi-VN"; u.voice = voice; u.rate = o.rate ?? 1; u.pitch = o.pitch ?? 1;
        if (k === pieces.length - 1) u.onend = () => res();
        u.onerror = (ev) => {
          if (cur !== my || ev.error === "interrupted" || ev.error === "canceled") return rej(abortErr());
          rej(new Error("Lỗi đọc: " + ev.error));
          speechSynthesis.cancel();
        };
        keep.push(u);
        speechSynthesis.speak(u);
      });
    });
    keep.length = 0;
  }

  // speak(text,{engine,rate,pitch,voice}) → resolve khi đọc xong; reject AbortError khi bị stop()/đọc chồng
  async function speak(text, o = {}) {
    stop();
    const t = clean(text);
    const my = { reject: null, timer: 0 };
    cur = my;
    if (!t) { cur = null; return; }
    const engine = o.engine || (engines().includes("native") ? "native" : "browser");
    try {
      await new Promise((res, rej) => {
        my.reject = rej;
        (engine === "native" ? speakNative : speakBrowser)(t, o, my).then(res, rej);
      });
    } finally { if (cur === my) settle(); else clearInterval(my.timer); }
  }

  function stop() {
    const c = cur;
    settle();
    if (c?.reject) c.reject(abortErr());
    if (hasBrowser()) speechSynthesis.cancel();
    plug("TextToSpeech")?.stop().catch(() => {});
  }

  // ---- giữ màn hình sáng
  let lock = null, wantAwake = false;
  async function grab() {
    if (!wantAwake || lock || document.visibilityState !== "visible" || !navigator.wakeLock) return;
    try { lock = await navigator.wakeLock.request("screen"); lock.addEventListener("release", () => { lock = null; }); } catch { lock = null; }
  }
  async function keepAwake(on) {
    wantAwake = !!on && S().keepAwake !== false;
    const ka = plug("KeepAwake");
    if (ka) { try { await (wantAwake ? ka.keepAwake() : ka.allowSleep()); return; } catch { /* rơi xuống wakeLock */ } }
    if (wantAwake) return grab();
    const l = lock; lock = null;
    await l?.release().catch(() => {});
  }
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") grab(); });

  // mở trình cài giọng (Android) khi không có giọng Việt
  function installVoices() { return plug("TextToSpeech")?.openInstall?.().catch(() => {}); }

  window.ML.tts = { engines, voices, speak, stop, clean, keepAwake, installVoices, split };
})();
