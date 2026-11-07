"""Exercise the production font allowlist over HTTP, including path rejection."""
import http.client
from pathlib import Path
import threading
import unittest
from server import Handler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parent


class Fonts(unittest.TestCase):
    def test_font_files_and_notices_are_served_without_opening_other_paths(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            files = {'BMJUA.ttf': 'font/ttf',
                     'NanumSquareRoundR.woff2': 'font/woff2',
                     'NanumSquareRoundB.woff2': 'font/woff2',
                     'NanumSquareRoundEB.woff2': 'font/woff2',
                     'OFL-BM-JUA.txt': 'text/plain; charset=utf-8',
                     'OFL-NanumSquareRound.txt': 'text/plain; charset=utf-8'}
            for name, mime in files.items():
                with self.subTest(name=name):
                    conn = http.client.HTTPConnection(*server.server_address)
                    conn.request('GET', '/assets/fonts/' + name)
                    response = conn.getresponse()
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.getheader('Content-Type'), mime)
                    self.assertEqual(response.read(), (ROOT / 'assets/fonts' / name).read_bytes())
                    conn.close()
            for path in ('/assets/fonts/../server.py', '/assets/fonts/missing.woff2', '/server.py'):
                conn = http.client.HTTPConnection(*server.server_address)
                conn.request('GET', path)
                self.assertEqual(conn.getresponse().status, 404)
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
