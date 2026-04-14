import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self._json({"msg": "hello from python", "path": self.path})

    def do_POST(self):
        body = self._body()
        self._json({"msg": "post received", "path": self.path, "body": body})

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length > 0 else {}

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
