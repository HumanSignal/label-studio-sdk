"""Offline mock of the two Label Studio endpoints, to validate tab_intersection.py."""
import json, re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# tab 583304 -> tasks 1..120 ; tab 584750 -> tasks 100..219 => overlap = 100..120 = 21
TABS = {
    583304: {"title": "Tab A", "ids": list(range(1, 121))},
    584750: {"title": "Tab B", "ids": list(range(100, 220))},
}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        m = re.match(r"^/api/dm/views/(\d+)/$", u.path)
        if m:
            vid = int(m.group(1))
            return self._send({"id": vid, "project": 280769,
                               "data": {"title": TABS[vid]["title"]},
                               "filter_group": {"conjunction": "and", "filters": []}})
        if u.path == "/api/tasks/":
            vid = int(q["view"][0])
            page = int(q.get("page", ["1"])[0])
            size = int(q.get("page_size", ["100"])[0])
            ids = TABS[vid]["ids"]
            chunk = ids[(page - 1) * size: page * size]
            return self._send({"count": len(ids), "next": None, "previous": None,
                               "tasks": [{"id": i} for i in chunk],
                               "results": [{"id": i} for i in chunk]})
        self._send({"detail": "not found"}, 404)

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8931), H).serve_forever()
