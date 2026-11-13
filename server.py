"""
Lightweight Web Server for YouTube Big Data Studio.
Serves the frontend dashboard and provides REST endpoints.
Runs natively using Python's standard library (no external dependencies required).
Run via: python server.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import http.server
import socketserver

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

class StudioHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return super().do_GET()
        elif self.path == "/api/data" or self.path == "/data.json":
            data_file = FRONTEND_DIR / "data.json"
            if data_file.exists():
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(data_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "data.json not found")
                return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/run-pipeline":
            print("[*] Web API triggered: Executing run_all.py in background...")
            try:
                python_exe = sys.executable
                subprocess.Popen([python_exe, str(PROJECT_ROOT / "run_all.py")])
                response = {
                    "status": "success",
                    "message": "Distributed Hadoop/Spark pipeline launched in background! Refreshing dashboard shortly."
                }
                status_code = 200
            except Exception as e:
                response = {"status": "error", "message": str(e)}
                status_code = 500

            body = json.dumps(response).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "Endpoint not found")

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_server(port: int = 5000):
    with ReusableTCPServer(("", port), StudioHTTPRequestHandler) as httpd:
        print("=" * 68)
        print("   YouTube Big Data Studio - Web Dashboard Active")
        print("=" * 68)
        print(f"   URL      : http://localhost:{port}")
        print(f"   Web Root : {FRONTEND_DIR}")
        print(f"   API      : http://localhost:{port}/api/data")
        print("=" * 68)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Server stopped cleanly.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    start_server(port)


