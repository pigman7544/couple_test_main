import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from rs_gpt import ROOT, ExperimentError, PROFILES, fixed_case, run_report, validate
from rs_gpt_budget import init_local_budget, local_budget
from rs_gpt_server import Handler


class RsGptTests(unittest.TestCase):
    token = "test-admin-token-" * 3
    births = {
        "a": {"date": "1992-03-18", "time": "", "gender": "male"},
        "b": {"date": "1992-04-30", "time": "", "gender": "female"},
    }
    def setUp(self):
        local = patch.dict("os.environ", {"RENDER": "false"})
        local.start()
        self.addCleanup(local.stop)

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, mode, profile="sol-61", token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return urlopen(Request(
            self.origin + "/api/rs-gpt",
            json.dumps({"mode": mode, "profile": profile}).encode(),
            headers,
        ), timeout=5)

    def post_admin(self, token=None, births=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return urlopen(Request(self.origin + "/api/rs-gpt/admin",
                               json.dumps(births or self.births).encode(), headers), timeout=5)

    def test_fixed_calculation(self):
        data, baseline = fixed_case()
        self.assertEqual([len(c["paragraphs"]) for c in baseline], [6, 12, 3])
        self.assertEqual(data["charts"]["a"]["pillars"],
                         dict(year="壬申", month="癸卯", day="癸巳", hour=None))
        self.assertEqual(data["charts"]["b"]["pillars"],
                         dict(year="壬申", month="甲辰", day="丙子", hour=None))
        facts = data["facts"]
        self.assertTrue(all(facts[f"{p}.palace"]["matches_other_day_master"] for p in "ab"))
        self.assertEqual([facts[f"{p}.partner"]["cross_ten_god"] for p in "ab"], ["정재", "정관"])
        self.assertEqual(facts["pair.palaces"]["direct_branch_relation_ids"], [])
        self.assertFalse(any(".hour." in ref for ref in facts))
        self.assertEqual({f["kind"] for f in facts.values() if "sources" in f},
                         {"육합", "삼합", "상형", "육해"})

    @patch("rs_gpt.urlopen")
    def test_no_key_mock_http_flow_and_live_disabled(self, provider):
        with urlopen(self.origin, timeout=5) as response:
            self.assertIn("전문 비교 내려받기", response.read().decode())
        with urlopen(self.origin + "/api/rs-gpt", timeout=5) as response:
            self.assertEqual(len(json.load(response)["baseline"]), 3)
        for profile in PROFILES:
            with self.post("mock", profile) as response:
                report = json.load(response)
            self.assertEqual(len(report["chapters"]), 3)
            self.assertEqual(report["mode"], "mock")
            self.assertEqual(report["metrics"], {"latency_ms": None, "usage": None})
        with patch.dict("os.environ", {"RS_GPT_LIVE": "1", "OPENAI_API_KEY": ""}):
            with self.assertRaises(HTTPError) as error:
                self.post("live")
            self.assertEqual(error.exception.code, 403)
        provider.assert_not_called()

    @patch("rs_gpt_server.render_budget")
    @patch("rs_gpt.urlopen")
    def test_render_identity_admin_and_failed_budget_block_upstream(self, provider, budget):
        token = "test-admin-token-" * 3
        config = {"RENDER": "true", "RENDER_SERVICE_ID": "srv-dc23purl550s7381llg0",
                  "RS_GPT_LIVE": "1", "OPENAI_API_KEY": "mock-transport-key",
                  "RS_GPT_ADMIN_TOKEN": token, "RS_GPT_BUDGET_DSN": "test-only"}
        budget.side_effect = ExperimentError("budget_store", "unavailable", 503)
        with patch.dict("os.environ", config):
            for supplied in (None, "incorrect"):
                with self.assertRaises(HTTPError) as error:
                    self.post_admin(supplied)
                self.assertEqual(error.exception.code, 403)
            with patch.dict("os.environ", {"RENDER_SERVICE_ID": "wrong-service"}):
                with self.assertRaises(HTTPError) as error:
                    self.post_admin(token)
                self.assertEqual(error.exception.code, 503)
            budget.assert_not_called()
            with self.assertRaises(HTTPError) as error:
                self.post_admin(token)
            self.assertEqual(json.load(error.exception)["code"], "budget_store")
        budget.assert_called_once_with(343_000)
        provider.assert_not_called()

    @patch("rs_gpt.urlopen")
    def test_responses_api_mock_transport_through_http(self, provider):
        sample = json.loads((ROOT / "rs_gpt_mock.json").read_text(encoding="utf-8"))["sol-61"]
        provider.return_value.__enter__.return_value.read.return_value = json.dumps({
            "status": "completed", "output": [{"type": "message", "content": [
                {"type": "output_text", "text": json.dumps(sample)}
            ]}], "usage": {"input_tokens": 1000, "input_tokens_details": {"cached_tokens": 500},
                          "output_tokens": 500},
        }).encode()
        with TemporaryDirectory() as folder:
            ledger = Path(folder) / "budget.sqlite"
            init_local_budget(ledger)
            with patch.dict("os.environ", {"RS_GPT_LIVE": "1", "OPENAI_API_KEY": "mock-transport-key",
                                           "RS_GPT_ADMIN_TOKEN": self.token,
                                           "RS_GPT_LOCAL_LEDGER": str(ledger)}):
                with self.post_admin(self.token) as response:
                    report = json.load(response)
                with self.assertRaises(HTTPError) as error:
                    self.post_admin(self.token)
                self.assertEqual(error.exception.code, 429)
            provider.assert_called_once()
        request = provider.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")
        self.assertFalse(body["store"])
        self.assertTrue(body["text"]["format"]["strict"])
        self.assertNotIn("1992", body["input"])
        self.assertEqual(body["model"], "gpt-6.2-sol")
        self.assertEqual(body["max_output_tokens"], 5500)
        self.assertIsNone(report["charts"]["a"]["pillars"]["hour"])
        self.assertIsNone(report["charts"]["b"]["pillars"]["hour"])
        self.assertEqual(report["metrics"]["usage"]["estimated_usd"], 0.00605)
        self.assertIsInstance(report["metrics"]["latency_ms"], int)

    @patch("rs_gpt_server.verify_render_ledger", return_value={
        "reservations": 1, "reserved_micro_usd": 343_000,
    })
    def test_ledger_check_requires_admin_and_works_with_live_disabled(self, verify):
        address = self.origin + "/api/rs-gpt/admin/ledger"
        config = {"RENDER_SERVICE_ID": "srv-dc23purl550s7381llg0",
                  "RS_GPT_ADMIN_TOKEN": self.token, "RS_GPT_LIVE": "0"}
        with patch.dict("os.environ", config):
            with self.assertRaises(HTTPError) as error:
                urlopen(address, timeout=5)
            self.assertEqual(error.exception.code, 403)
            verify.assert_not_called()
            request = Request(address, headers={"Authorization": f"Bearer {self.token}"})
            with urlopen(request, timeout=5) as response:
                self.assertEqual(json.load(response), verify.return_value)
        verify.assert_called_once_with()

    def test_admin_auth_normalizes_configured_token_with_live_disabled(self):
        address = self.origin + "/api/rs-gpt/admin"
        request = Request(address, headers={"Authorization": f"Bearer {self.token}"})
        config = {"RS_GPT_ADMIN_TOKEN": f"  {self.token}\n", "RS_GPT_LIVE": "0"}
        with patch.dict("os.environ", config):
            with urlopen(request, timeout=5) as response:
                self.assertEqual(response.status, 200)
                self.assertFalse(json.load(response)["live_enabled"])
            with self.assertRaises(HTTPError) as error:
                urlopen(address, timeout=5)
            self.assertEqual(error.exception.code, 403)

    def test_admin_mixed_birth_times(self):
        config = {"RS_GPT_LIVE": "1", "OPENAI_API_KEY": "mock-transport-key",
                  "RS_GPT_ADMIN_TOKEN": self.token, "RS_GPT_LOCAL_LEDGER": "test-only"}
        births = {**self.births, "a": {**self.births["a"], "date": "1992-03-19", "time": "09:17"}}
        with patch.dict("os.environ", config), patch("rs_gpt_server.run_report", return_value={}):
            with self.post_admin(self.token, births) as response:
                data = json.load(response)
            self.assertIn("a.hour.stem", data["facts"])
            self.assertNotIn("b.hour.stem", data["facts"])
            self.assertNotEqual(data["charts"]["a"]["pillars"]["day"], "癸巳")
            births["a"]["date"] = "1992-02-30"
            with self.assertRaises(HTTPError) as error:
                self.post_admin(self.token, births)
            self.assertEqual(error.exception.code, 400)

    def test_missing_ledger_does_not_reset_allowance(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "missing.sqlite"
            with patch.dict("os.environ", {"RS_GPT_LOCAL_LEDGER": str(path)}):
                with self.assertRaises(ExperimentError) as error, local_budget(343_000):
                    self.fail("Budget must fail closed")
            self.assertEqual(error.exception.code, "budget_store")
            self.assertFalse(path.exists())

    def test_rejects_unknown_reference_and_uncited_interaction(self):
        facts, _ = fixed_case()
        for ref, added_text in (("a.hour.stem", ""), ("a.day.stem", " 육충이 확인됩니다.")):
            sample = json.loads((ROOT / "rs_gpt_mock.json").read_text(encoding="utf-8"))["sol-61"]
            paragraph = sample["chapters"][0]["paragraphs"][0]
            paragraph["evidence_ids"].append(ref)
            paragraph["text"] += added_text
            with self.assertRaises(ExperimentError) as error:
                validate(sample, facts["facts"])
            self.assertEqual(error.exception.code, "grounding")

    @patch("rs_gpt.request_openai", return_value={"status": "incomplete"})
    def test_reports_incomplete_without_returning_prose(self, request):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "mock-transport-key"}):
            with self.assertRaises(ExperimentError) as error:
                run_report("sol-61", "live", live_enabled=True)
        self.assertEqual(error.exception.code, "incomplete")
        self.assertIsInstance(error.exception.metrics["latency_ms"], int)

