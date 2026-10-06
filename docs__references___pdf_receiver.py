from http.server import BaseHTTPRequestHandler, HTTPServer
OUT = r"I:\\Projects\\20260522-LSG-WRR\\docs\\references\\Fraehr_2023_WRR_Fast_Accurate_Hybrid_Floodplain_LSG.pdf"
class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(n)
        open(OUT, "wb").write(data)
        self.send_response(200); self._cors(); self.end_headers()
        msg = f"wrote {len(data)}"
        self.wfile.write(msg.encode())
        print(msg, flush=True)
    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)
print("listening 18765", flush=True)
HTTPServer(("127.0.0.1", 18765), H).serve_forever()
