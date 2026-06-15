"""
Server local cho giao diện chat Thầy Trung.
- Phục vụ chat.html ở /
- Proxy /invocations và /health sang agent (cổng 8080) → tránh CORS.

Chạy:  python3 serve_local.py
Mở:    http://localhost:3000
"""
import http.server
import socketserver
import urllib.request
import os

UI_PORT = 3000
AGENT_URL = "http://localhost:8080"
HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HERE, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html", "/chat.html"):
            self.path = "/chat.html"
            return super().do_GET()
        if self.path == "/health":
            return self._proxy("GET")
        return super().do_GET()

    def do_POST(self):
        if self.path == "/invocations":
            return self._proxy("POST")
        self.send_error(404)

    def _proxy(self, method):
        try:
            body = None
            if method == "POST":
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
            req = urllib.request.Request(
                AGENT_URL + self.path, data=body, method=method,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(f'{{"status":"error","response":"Proxy lỗi: {e}"}}'.encode())

    def log_message(self, *args):
        pass  # giữ console gọn


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", UI_PORT), Handler) as httpd:
        print(f"✅ Giao diện chat: http://localhost:{UI_PORT}")
        print(f"   (proxy → agent ở {AGENT_URL})")
        print("   Ctrl+C để dừng.")
        httpd.serve_forever()
