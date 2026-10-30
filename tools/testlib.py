"""Shared helpers for the site's Playwright checks: serve the repo locally and open pages with
every third-party request blocked (pixels, fonts, Stripe), so tests are fast and send nothing."""
import contextlib
import functools
import http.server
import os
import socket
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@contextlib.contextmanager
def serve(root=ROOT):
    """Serve `root` on a free localhost port. Yields the base URL (no trailing slash).
    Unknown paths get /404.html when it exists, like GitHub Pages."""
    class H(_Quiet):
        def translate_path(self, path):
            # GitHub Pages serves /shop as /shop.html; do the same so extensionless ad URLs are testable.
            fs = super().translate_path(path)
            if not os.path.exists(fs) and os.path.exists(fs + ".html"):
                return fs + ".html"
            return fs

        def send_error(self, code, message=None, explain=None):
            p = os.path.join(root, "404.html")
            if code == 404 and os.path.exists(p):
                body = open(p, "rb").read()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            super().send_error(code, message, explain)
    handler = functools.partial(H, directory=root)
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    class Server(http.server.ThreadingHTTPServer):
        def handle_error(self, request, client_address):
            pass   # browsers drop connections (aborted media, closed pages); not a test failure
    httpd = Server(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()


def block_third_party(context, base):
    """Abort every request that isn't to the local server."""
    def route(r):
        if r.request.url.startswith(base):
            r.continue_()
        else:
            r.abort()
    context.route("**/*", route)
