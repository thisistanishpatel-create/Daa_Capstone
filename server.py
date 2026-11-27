"""
Huffman Compressor - web server
================================
Serves the website in web/ and runs the REAL Huffman code (huffman.py) for the website.

  python server.py          -> opens http://localhost:8000
  python server.py 5000     -> use another port

API (used by the website):
  GET  /api/ping       -> {"engine": "python"}
  POST /api/compress   body = text (UTF-8)       -> .huf file bytes
  POST /api/restore    body = .huf file bytes    -> original text

Only the Python standard library is used (nothing to install).
"""
import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import huffman

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
MAX_BYTES = 3 * 1024 * 1024        # 3 MB limit, same as the website


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/ping":
            return self.send(200, json.dumps({"engine": "python", "file": "huffman.py"}), "application/json")
        if path in ("/", "/index.html"):
            with open(os.path.join(WEB_DIR, "index.html"), "rb") as f:
                return self.send(200, f.read(), "text/html; charset=utf-8")
        self.send(404, "Not found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BYTES:
            return self.send(413, "This file is larger than 3 MB. Please choose a smaller text file.")
        body = self.rfile.read(length)
        path = self.path.split("?")[0]
        if path == "/api/compress":
            try:
                text = body.decode("utf-8")
            except UnicodeDecodeError:
                return self.send(400, "This file is not UTF-8 text.")
            blob = huffman.compress_bytes(text)[0]           # <- Huffman compression (huffman.py)
            return self.send(200, blob, "application/octet-stream")
        if path == "/api/restore":
            try:
                text = huffman.decompress_bytes(body)         # <- Huffman decompression (huffman.py)
            except ValueError:
                return self.send(400, "This is not a Huffman file made by this tool (the HUF1 header is missing).")
            except Exception:
                return self.send(400, "The file is damaged and cannot be restored.")
            return self.send(200, text)
        self.send(404, "Not found")

    def log_message(self, fmt, *args):
        print("  " + (fmt % args))


def make_server(port=8000):
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = None
    for p in range(port, port + 10):                # if the port is busy, try the next one
        try:
            server = make_server(p)
            break
        except OSError:
            continue
    if server is None:
        sys.exit("Could not find a free port. Close other programs or run: python server.py 5000")
    url = f"http://localhost:{server.server_address[1]}"
    print(f"Huffman Compressor running at {url}\nPress Ctrl+C to stop.")
    threading.Timer(0.8, webbrowser.open, [url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
