window.ML = window.ML || {};
(() => {
  let deferred = null, inited = false;
  const subs = [];
  const emit = () => subs.forEach(fn => { try { fn(!!deferred); } catch (e) {} });

  ML.pwa = {
    init() {
      if (inited) return; inited = true;
      addEventListener('beforeinstallprompt', e => { e.preventDefault(); deferred = e; emit(); });
      addEventListener('appinstalled', () => { deferred = null; emit(); ML.toast?.('Đã cài MythLab'); });
      if (window.Capacitor || !/^https?:$/.test(location.protocol) || !('serviceWorker' in navigator)) return;
      // lần cài đầu sw.js gọi clients.claim() → controller có ngay; chỉ báo "bản mới" khi trước đó đã có SW
      const had = !!navigator.serviceWorker.controller;
      const go = () => navigator.serviceWorker.register('sw.js', {scope: './'}).then(reg => {
        reg.addEventListener('updatefound', () => {
          const w = reg.installing;
          w && w.addEventListener('statechange', () => {
            if (w.state === 'activated' && had) ML.toast?.('Đã có bản mới — tải lại trang để cập nhật');
          });
        });
      }).catch(e => console.warn('SW:', e));
      document.readyState === 'complete' ? go() : addEventListener('load', go, {once: true});
    },
    installAvailable: () => !!deferred,
    async install() {
      if (!deferred) return false;
      const e = deferred; deferred = null; emit();
      e.prompt();
      const r = await e.userChoice.catch(() => null);
      return r?.outcome === 'accepted';
    },
    onInstallChange(fn) { subs.push(fn); },
    standalone: () => matchMedia('(display-mode: standalone)').matches || navigator.standalone === true,
  };
})();
