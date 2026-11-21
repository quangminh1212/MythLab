"""Tiny static host for the e2e scripts whose document root can be switched while it keeps listening on the
same port (the service-worker upgrade test serves the old reader/static, then the new web/dist, on one origin).

Never use 8765 or 18765 here: those belong to the running MythLab servers.
"""
import http.server
import mimetypes
import os
import threading
import urllib.parse

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/javascript", ".js")


class Host:
    def __init__(self, root, port):
        if port in (8765, 18765):
            raise ValueError("port reserved for the running MythLab servers")
        self.root = os.path.abspath(root)
        self.port = port
        self.hits = []
        host = self

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                path = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
                host.hits.append(path)
                rel = path.lstrip("/") or "index.html"
                full = os.path.abspath(os.path.join(host.root, rel))
                if not full.startswith(host.root) or not os.path.isfile(full):
                    self.send_response(404)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                with open(full, "rb") as f:
                    body = f.read()
                ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(body)

            do_HEAD = do_GET

        class Srv(http.server.ThreadingHTTPServer):
            daemon_threads = True

        self.srv = Srv(("127.0.0.1", port), H)
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.srv.shutdown()
        self.srv.server_close()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.port}"
