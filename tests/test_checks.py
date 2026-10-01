import importlib.util
import json
import socket
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

_spec = importlib.util.spec_from_file_location("small_checks", Path(__file__).parent.parent / "cases" / "small" / "checks.py")
checks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checks)


class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"status": "ok"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class WaitHealthy(unittest.TestCase):
    def test_late_start_is_waited_for(self):
        port = free_port()
        servers = []

        def start():
            server = ThreadingHTTPServer(("127.0.0.1", port), Health)
            servers.append(server)
            threading.Thread(target=server.serve_forever, daemon=True).start()

        threading.Timer(1.5, start).start()
        started = time.monotonic()
        try:
            self.assertTrue(checks.wait_healthy(f"http://127.0.0.1:{port}", limit=10))
            self.assertGreater(time.monotonic() - started, 1)
        finally:
            time.sleep(0.1)
            for server in servers:
                server.shutdown()
                server.server_close()

    def test_nothing_listening_gives_up(self):
        self.assertFalse(checks.wait_healthy(f"http://127.0.0.1:{free_port()}", limit=2))


if __name__ == "__main__":
    unittest.main()
