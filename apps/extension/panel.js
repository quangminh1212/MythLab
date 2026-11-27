// The site cannot be framed (frame-ancestors 'none'), so the panel itself navigates to it.
const URL_ = 'https://myth.xlabrnd.com/';
if (navigator.onLine) location.replace(URL_);
else {
  document.getElementById('m').textContent = 'Không có mạng. Mở lại khi đã kết nối.';
  addEventListener('online', () => location.replace(URL_));
}
