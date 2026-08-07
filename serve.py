#!/usr/bin/env python3
"""Local dev server that mimics Vercel's cleanUrls behavior.

/about          -> about.html
/locations      -> locations/index.html  (or locations.html if that existed)
/locations/     -> locations/index.html
/assets/x.css   -> served as-is (has an extension already)
"""
import http.server
import os
import socketserver
import urllib.parse

PORT = 8936
ROOT = os.path.dirname(os.path.abspath(__file__))


class CleanUrlHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        path = urllib.parse.unquote(parsed.path)

        if path != "/" and not path.endswith("/"):
            fs_path = os.path.join(ROOT, path.lstrip("/"))
            last_segment = path.rsplit("/", 1)[-1]
            has_extension = "." in last_segment

            if not has_extension:
                html_candidate = fs_path + ".html"
                index_candidate = os.path.join(fs_path, "index.html")
                if os.path.isfile(html_candidate):
                    self.path = path + ".html" + (("?" + parsed.query) if parsed.query else "")
                elif os.path.isdir(fs_path) and os.path.isfile(index_candidate):
                    self.path = path + "/" + (("?" + parsed.query) if parsed.query else "")

        return super().do_GET()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CleanUrlHandler) as httpd:
        print(f"Serving {ROOT} at http://localhost:{PORT} (clean URLs enabled)")
        httpd.serve_forever()
