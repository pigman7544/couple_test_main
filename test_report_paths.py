"""Report coverage and loopback HTTP checks; no production matching rules changed."""
import hashlib
import http.client
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

from engine import person
from matcher import DB, rank
from narrative import describe
from relationship_v08 import relation
from server import Handler, MAX_BODY, ThreadingHTTPServer, compute
from story_report import make_report


SAMPLE = {
    'a': {'date': '1992-03-18', 'time': '16:00', 'calendar': 'solar', 'gender': 'female'},
    'b': {'date': '1992-04-30', 'time': '01:00', 'calendar': 'solar', 'gender': 'male'},
}
SECTIONS = ('tagline', 'story', 'roles', 'saju_a', 'crisis', 'scene', 'tip', 'ending')
EXPECTED_IDS = {'c01', 'c02', 'c03', 'c06', 'c10', 'c11', 'c13', 'c18',
                'f01', 'f02', 'f03', 'f04'}


class ReportPaths(unittest.TestCase):
    def test_all_twelve_reports_without_astrology(self):
        self.assertEqual({c['id'] for c in DB}, EXPECTED_IDS)
        for with_time in (True, False):
            a = person(1992, 3, 18, 16 if with_time else None)
            b = person(1992, 4, 30, 1 if with_time else None)
            rel = relation(a, b)
            with patch.dict(sys.modules, {'astrology': None}):
                for couple in DB:
                    with self.subTest(couple=couple['id'], with_time=with_time):
                        story = describe(rel['vector'], couple['id'])
                        report = make_report(a, b, rel, couple, story)
                        for key in SECTIONS:
                            self.assertTrue(report[key], key)
                        self.assertTrue(report['questions'])
                        text = json.dumps(report, ensure_ascii=False)
                        self.assertNotIn('태양궁', text)
                        self.assertNotIn('별자리', text)

    def test_legacy_baek_heo_envelopes_match_pre_fix_baseline(self):
        # Captured from main b446e24 before modifying either production file.
        path = Path(__file__).parent / 'tests/fixtures/baek_heo_responses.json'
        for fixture in json.loads(path.read_text(encoding='utf8')):
            with self.subTest(case=fixture['case'], unlock=fixture['unlock']):
                # Full c06 prose is intentionally revised; still verify the exact historical
                # response envelope using the original report on the protected path.
                import story_report
                from unittest.mock import patch
                with patch('server.make_report', side_effect=story_report._v66_make_report):
                    response = compute(fixture['payload'], unlock=fixture['unlock'])
                self.assertEqual(response['couple']['id'], 'c06')
                raw = json.dumps(response, ensure_ascii=False, sort_keys=True).encode('utf8')
                self.assertEqual(hashlib.sha256(raw).hexdigest(), fixture['sha256'])


class RecordingHandler(Handler):
    logs = []

    def log_message(self, fmt, *args):
        # Keep the real BaseHTTPRequestHandler.log_error signature in use.
        self.logs.append(fmt % args)


class HttpPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), RecordingHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=5)

    def post(self, endpoint, payload=None, raw=None):
        body = raw if raw is not None else json.dumps(payload).encode('utf8')
        connection = http.client.HTTPConnection(*self.httpd.server_address, timeout=5)
        try:
            connection.request('POST', endpoint, body=body,
                               headers={'Content-Type': 'application/json'})
            response = connection.getresponse()
            data = response.read()
            self.assertEqual(response.getheader('Content-Type'), 'application/json; charset=utf-8')
            self.assertEqual(response.getheader('Cache-Control'), 'no-store')
            self.assertEqual(int(response.getheader('Content-Length')), len(data))
            return response.status, json.loads(data)
        finally:
            connection.close()

    def check_success(self, payload, expected_id):
        for endpoint in ('/api/match', '/api/test-unlock'):
            with self.subTest(endpoint=endpoint, couple=expected_id):
                status, data = self.post(endpoint, payload)
                self.assertEqual(status, 200, data)
                self.assertEqual(data['couple']['id'], expected_id)
                self.assertEqual(data['has_art'], expected_id == 'c06')
                if endpoint == '/api/match':
                    self.assertIn('preview', data)
                    self.assertNotIn('full_report', data)
                else:
                    self.assertTrue(data['test_mode'])
                    for key in SECTIONS:
                        self.assertTrue(data['full_report'][key], key)

    def test_real_matching_preview_and_unlock(self):
        # Real dates and unmodified rank(), including the formerly failing path.
        self.check_success(SAMPLE, 'c06')
        no_time = {key: dict(value, time='') for key, value in SAMPLE.items()}
        self.check_success(no_time, 'c06')
        self.check_success({'a': {'date': '2010-05-06'},
                            'b': {'date': '2007-04-02'}}, 'c01')

    def test_each_type_over_http_with_controlled_selection(self):
        # Force only winner selection, since not all 12 types have known date fixtures.
        # Person calculation, relation, narrative, report, JSON and HTTP remain real.
        a, b = person(1992, 3, 18, 16), person(1992, 4, 30, 1)
        ranked = rank(relation(a, b)['vector'])
        for couple_id in sorted(EXPECTED_IDS):
            ordered = sorted(ranked, key=lambda item: item[1] != couple_id)
            with patch('server.rank', return_value=ordered):
                self.check_success(SAMPLE, couple_id)

    def test_invalid_requests_return_400_json(self):
        invalid_payloads = [None, [], {}, {'a': None, 'b': {}},
                            {'a': {'date': 123}, 'b': SAMPLE['b']},
                            {'a': dict(SAMPLE['a'], time=123), 'b': SAMPLE['b']},
                            {'a': dict(SAMPLE['a'], date='2024-02-30'), 'b': SAMPLE['b']},
                            {'a': dict(SAMPLE['a'], time='25:00'), 'b': SAMPLE['b']}]
        for endpoint in ('/api/match', '/api/test-unlock'):
            for payload in invalid_payloads:
                with self.subTest(endpoint=endpoint, payload=payload):
                    status, data = self.post(endpoint, payload)
                    self.assertEqual(status, 400)
                    self.assertTrue(data['error'])
            for raw in (b'{', b'', b'\xff', b'x' * (MAX_BODY + 1)):
                with self.subTest(endpoint=endpoint, raw_length=len(raw)):
                    status, data = self.post(endpoint, raw=raw)
                    self.assertEqual(status, 400)
                    self.assertTrue(data['error'])

    def test_unexpected_errors_return_500_json_and_server_recovers(self):
        for endpoint in ('/api/match', '/api/test-unlock'):
            with self.subTest(endpoint=endpoint):
                RecordingHandler.logs.clear()
                with patch('server.compute', side_effect=RuntimeError('internal-test-detail')):
                    status, data = self.post(endpoint, SAMPLE)
                self.assertEqual(status, 500)
                self.assertEqual(data, {'error': '계산 중 오류가 발생했습니다. 입력값을 확인해 주세요.'})
                self.assertNotIn('internal-test-detail', json.dumps(data))
                self.assertTrue(any('RuntimeError: internal-test-detail' in log
                                    for log in RecordingHandler.logs))
        self.check_success(SAMPLE, 'c06')

    def test_baek_heo_cards_still_served(self):
        root = Path(__file__).parent
        for name in ('baek_heo_title.png', 'baek_heo_plain.png'):
            connection = http.client.HTTPConnection(*self.httpd.server_address, timeout=5)
            try:
                connection.request('GET', '/assets/' + name)
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(response.getheader('Content-Type'), 'image/png')
                self.assertEqual(response.read(), (root / 'assets' / name).read_bytes())
            finally:
                connection.close()


if __name__ == '__main__':
    unittest.main()
