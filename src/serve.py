#!/usr/bin/env python3
"""Local preview of public/ with Vercel-style clean URLs (/prices -> prices.html).

Run:  python3 src/serve.py [port]   (default 8000)
"""
import http.server
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")


class CleanUrlHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_head(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        local = os.path.join(ROOT, path.lstrip("/"))
        if not os.path.splitext(path)[1] and not os.path.isdir(local) and os.path.isfile(local + ".html"):
            self.path = path + ".html"
        elif not os.path.exists(local):
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(ROOT, "404.html"), "rb") as f:
                self.wfile.write(f.read())
            return None
        return super().send_head()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Serving {ROOT} at http://localhost:{port}")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), CleanUrlHandler).serve_forever()
