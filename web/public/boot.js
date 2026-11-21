/* MythLab boot script: classic, synchronous, loaded in <head> before the stylesheet paints.
   1. Sets <html data-theme / data-scheme> from the stored settings so the first paint has the right colours.
   2. Shows the boot error screen ("Không tải được ứng dụng") when the app module fails to load or never starts.
   Kept as a file (not inline) so a strict Content-Security-Policy stays possible. */
(function () {
  'use strict';
  var root = document.documentElement;
  var s = {};
  try {
    var rawSettings = localStorage.getItem('mythlab.settings') || localStorage.getItem('xlab.settings');
    if (rawSettings) s = JSON.parse(rawSettings) || {};
  } catch (e) {
    s = {};
  }
  var theme = ['light', 'sepia', 'dark', 'auto'].indexOf(s.theme) >= 0 ? s.theme : 'light';
  if (theme === 'sepia' && !s.ui2) theme = 'light';
  var scheme = theme;
  if (theme === 'auto') {
    var dark = false;
    try {
      dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    } catch (e) {
      dark = false;
    }
    scheme = dark ? 'dark' : 'light';
  }
  root.setAttribute('data-theme', theme);
  root.setAttribute('data-scheme', scheme);

  function fail() {
    if (window.__mlBooted) return;
    var el = document.getElementById('boot-error');
    if (el) el.hidden = false;
    var view = document.getElementById('view');
    if (view) view.setAttribute('aria-busy', 'false');
  }
  window.__mlBootFail = fail;
  // a <script> or <link> that fails to load does not bubble: listen in the capture phase
  window.addEventListener(
    'error',
    function (e) {
      var t = e && e.target;
      if (t && t !== window && t.tagName === 'SCRIPT') fail();
    },
    true
  );
  window.__mlBootTimer = setTimeout(fail, 15000);
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (t && t.closest && t.closest('#boot-retry')) location.reload();
  });
})();
