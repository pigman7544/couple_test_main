import json
import threading
import unittest
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from rs_gpt import ROOT, ExperimentError, PROFILES, fixed_case, run_report, validate
from rs_gpt_budget import (
    MONTHLY_MICRO_USD, RENDER_SERVICE_ID, check_budget, init_local_budget,
    local_budget, month_start, monthly_call_limit,
)
from matcher import DB
from rs_gpt_server import DIAGNOSTIC_API, EDITORIAL_SAMPLE_API, GroundingDiagnostic, Handler


class RsGptBudgetTests(unittest.TestCase):
    def test_target_override_preserves_default_and_separate_spend_cap(self):
        with patch.dict("os.environ", {
            "RENDER": "true", "RENDER_SERVICE_ID": "other",
            "RS_GPT_MONTHLY_CALLS": "5",
        }):
            self.assertEqual(monthly_call_limit(), 3)
            with self.assertRaisesRegex(ExperimentError, "한도"):
                check_budget(3, 1_029_000, 300, 343_000)
            with patch.dict("os.environ", {"RENDER_SERVICE_ID": RENDER_SERVICE_ID}):
                self.assertEqual(monthly_call_limit() - 3, 2)
                check_budget(3, 1_029_000, 300, 343_000)
                check_budget(4, 1_372_000, 300, 343_000)
                with self.assertRaisesRegex(ExperimentError, "한도"):
                    check_budget(5, 1_715_000, 300, 343_000)
                check_budget(0, MONTHLY_MICRO_USD - 343_000, 300, 343_000)
                with self.assertRaisesRegex(ExperimentError, "한도"):
                    check_budget(0, MONTHLY_MICRO_USD - 342_999, 300, 343_000)
                with self.assertRaisesRegex(ExperimentError, "5분"):
                    check_budget(3, 1_029_000, 299, 343_000)
                with patch.dict("os.environ", {"RS_GPT_MONTHLY_CALLS": "invalid"}):
                    self.assertEqual(monthly_call_limit(), 3)

    def test_existing_month_boundary_in_korea(self):
        kst = timezone(timedelta(hours=9))
        rollover = datetime(2026, 12, 1, 9, tzinfo=kst)
        self.assertEqual(month_start(rollover - timedelta(microseconds=1)),
                         datetime(2026, 11, 1, tzinfo=timezone.utc))
        self.assertEqual(month_start(rollover), rollover)


class RsGptTests(unittest.TestCase):
    token = "test-admin-token-" * 3
    births = {
        "a": {"name": "민준", "date": "1992-03-18", "time": "", "gender": "male"},
        "b": {"name": "서연", "date": "1992-04-30", "time": "", "gender": "female"},
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

    @patch("rs_gpt.validate")
    @patch("rs_gpt.urlopen")
    def test_responses_api_mock_transport_through_http(self, provider, validator):
        # The legacy comparison sample is only used to test API transport.
        validator.side_effect = lambda manuscript, facts, names, couple: validate(manuscript, facts)
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
        self.assertEqual(json.loads(body["input"])["names"], {"a": "민준", "b": "서연"})
        self.assertIn((ROOT / "rs_gpt_rules_v3.md").read_text(encoding="utf-8-sig"), body["instructions"])
        chapter_three_rules = body["instructions"].split("## 3장 작품 커플 소개", 1)[1]
        expected_order = ("첫 문장", "couple.story_beats", "실제 명식", "기억에 남는 한 문장")
        positions = [chapter_three_rules.index(rule) for rule in expected_order]
        self.assertEqual(positions, sorted(positions))
        for rule in ("막연한 칭찬", "이번 입력에 맞춰 새로 쓴다", "최대 2개"):
            self.assertIn(rule, chapter_three_rules)
        self.assertNotIn("서로를 아끼는 방식은 다르지만", body["instructions"])
        for example in ("윤하", "도현", "엘리자베스"):
            self.assertNotIn(example, body["instructions"])
        selected = json.loads(body["input"])["couple"]
        self.assertEqual(selected["id"], report["couple"]["id"])
        self.assertTrue(selected["story_beats"])
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

    @patch("rs_gpt_server.run_report")
    @patch("rs_gpt_server.verify_render_ledger")
    def test_admin_readiness_reports_config_blockers_without_generation(self, ledger, report):
        address = self.origin + "/api/rs-gpt/admin"
        request = Request(address, headers={"Authorization": f"Bearer {self.token}"})
        config = {"RENDER": "true", "RENDER_SERVICE_ID": "srv-dc23purl550s7381llg0",
                  "RS_GPT_ADMIN_TOKEN": self.token, "RS_GPT_LIVE": "1",
                  "OPENAI_API_KEY": "test-key", "RS_GPT_BUDGET_DSN": "test-dsn"}
        for changes, blockers in (
            ({}, []),
            ({"RS_GPT_LIVE": "0"}, ["live_off"]),
            ({"OPENAI_API_KEY": " "}, ["provider_key_missing"]),
            ({"RS_GPT_BUDGET_DSN": ""}, ["render_ledger_missing"]),
            ({"RENDER_SERVICE_ID": "another-service"}, ["wrong_render_service"]),
        ):
            with self.subTest(changes=changes), patch.dict("os.environ", {**config, **changes}, clear=True):
                with urlopen(request, timeout=5) as response:
                    body = json.load(response)
                    self.assertEqual(response.headers["Cache-Control"], "no-store")
                    self.assertEqual(body["live_enabled"], not blockers)
                    self.assertEqual(body["live_blockers"], blockers)
                with self.assertRaises(HTTPError) as error:
                    urlopen(address, timeout=5)
                self.assertEqual(error.exception.code, 403)
                self.assertNotIn("live_blockers", json.load(error.exception))
                if blockers:
                    with self.assertRaises(HTTPError) as error:
                        self.post_admin(self.token)
                    self.assertEqual(error.exception.code, 503)
        ledger.assert_not_called()
        report.assert_not_called()

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

    @patch("rs_gpt.urlopen")
    def test_admin_preview_with_live_disabled_validates_names(self, provider):
        config = {"RS_GPT_ADMIN_TOKEN": self.token, "RS_GPT_LIVE": "0"}
        data = {"mode": "preview", "a": {"name": "민준", "date": "1992-03-18"},
                "b": {"name": "서연", "date": "1992-04-30", "time": "09:17"}}
        with patch.dict("os.environ", config):
            with self.post_admin(self.token, data) as response:
                result = json.load(response)
            self.assertEqual(result["names"], {"a": "민준", "b": "서연"})
            self.assertIsNone(result["charts"]["a"]["pillars"]["hour"])
            self.assertIsNotNone(result["charts"]["b"]["pillars"]["hour"])
            self.assertNotIn("chapters", result)
            example = result
            data["a"] = {"name": "지우", "date": "1985-01-11", "time": "16:00"}
            data["b"] = {"name": "하늘", "date": "1992-04-30", "time": "01:00"}
            with self.post_admin(self.token, data) as response:
                different = json.load(response)
            self.assertEqual(different["names"], {"a": "지우", "b": "하늘"})
            self.assertNotEqual(different["charts"]["a"], example["charts"]["a"])
            self.assertNotEqual(different["facts"]["a.day.stem"], example["facts"]["a.day.stem"])
            self.assertEqual(different["couple"]["id"], "c06")
            self.assertEqual(different["art"], {v: f"/assets/baek_heo_{v}.png" for v in ("title", "plain")})
            for variant in ("title", "plain"):
                with urlopen(self.origin + different["art"][variant], timeout=5) as response:
                    self.assertEqual(response.headers.get_content_type(), "image/png")
                    self.assertTrue(response.read().startswith(b"\x89PNG\r\n\x1a\n"))
            data["a"]["name"] = "<img>"
            with self.assertRaises(HTTPError) as error:
                self.post_admin(self.token, data)
            self.assertEqual(error.exception.code, 400)
        provider.assert_not_called()

    @patch("rs_gpt.urlopen")
    def test_free_preview_only_displays_verified_art_for_selected_identity(self, provider):
        config = {"RS_GPT_ADMIN_TOKEN": self.token, "RS_GPT_LIVE": "0"}
        births = {**self.births, "mode": "preview"}
        with patch.dict("os.environ", config):
            for couple_id, stem in (("c01", "c01"), ("c06", "baek_heo"), ("c11", None)):
                selected = next(c for c in DB if c["id"] == couple_id)
                unrelated_art = {"title": "/assets/baek_heo_title.png", "plain": "/assets/baek_heo_plain.png"}
                ranked = [(0, couple_id, selected)]
                with patch("rs_gpt_server.match_inputs", return_value=(None,) * 5 + (ranked, unrelated_art)):
                    with self.post_admin(self.token, births) as response:
                        result = json.load(response)
                self.assertEqual(result["couple"], {key: selected[key] for key in ("id", "name", "work")})
                expected = {v: f"/assets/{stem}_{v}.png" for v in ("title", "plain")} if stem else None
                self.assertEqual(result["art"], expected)
                self.assertNotIn("chapters", result)
                for path in (expected or {}).values():
                    with urlopen(self.origin + path, timeout=5) as image:
                        self.assertEqual(image.read(), (ROOT / path.lstrip("/")).read_bytes())
            with urlopen(self.origin + "/rs-gpt/admin", timeout=5) as response:
                html = response.read().decode()
                self.assertIn("이 작품의 커플 일러스트는 아직 지원하지 않아요.", html)
                self.assertIn("default-src 'none'", response.headers["Content-Security-Policy"])
                self.assertIn("item.textContent = value", html)
        provider.assert_not_called()

    def test_personalized_chapters_check_term_density_and_selected_work(self):
        names = {"a": "민준", "b": "서연"}
        couple = {"work": "춘향전", "name": "춘향·이몽룡"}
        facts = {"pair": {"kind": "육충"}, "shape": {"kind": "상형"}}
        paragraphs = [
            ["민준님은 새로운 생각을 곧바로 이야기하는 편으로 읽을 수 있어요.",
             "서연님은 충분히 생각할 시간을 가질 때 마음이 놓일 수 있어요."],
            ["두 사람은 서로의 방식을 확인할 때 대화가 쉬워져요. 육충과 상형이 함께 나타납니다.",
             "가령 마음이 급한 날이라면 각자 원하는 것을 한 가지씩 이야기하고 상대의 말을 먼저 들어볼 수 있어요."],
            ["두 사람을 떠올리게 하는 작품은 춘향전이고, 작품 속 커플은 춘향·이몽룡이에요.",
             "오늘은 상대가 어떤 말을 듣고 싶은지 조용히 물어보세요."],
        ]
        manuscript = {"chapters": [
            {"title": "우리 둘의 이야기", "paragraphs": [
                {"text": line, "evidence_ids": ["pair", "shape"]} for line in chapter
            ]} for chapter in paragraphs
        ]}
        self.assertEqual(validate(manuscript, facts, names, couple)["paragraphs"], 6)
        with self.assertRaises(ExperimentError):
            validate(manuscript, facts, names, {"work": "백사전", "name": "백소정·허선"})
        with self.assertRaises(ExperimentError):
            validate(manuscript, facts, {**names, "a": "다른이름"}, couple)
        manuscript["chapters"][1]["paragraphs"][0]["text"] += " 일지에는 육충과 상형이 함께 나타납니다."
        with self.assertRaises(ExperimentError) as error:
            validate(manuscript, facts, names, couple)
        self.assertEqual(error.exception.diagnostic["category"], "expression")
        self.assertEqual(error.exception.diagnostic["rule"], "technical_term_density")

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
            self.assertEqual(error.exception.diagnostic["category"], "evidence")
            self.assertEqual(error.exception.diagnostic["rule"],
                             "invalid_evidence_ids" if ref == "a.hour.stem" else "uncited_technical_term")

    def test_grounding_variants_and_wrong_attributions(self):
        payload, _ = fixed_case()
        facts = payload["facts"]
        cases = [
            ("둘째의 연간은 임수이며 칠살로 읽습니다.", "b.year.stem", None),
            ("둘째의 연간은 임(壬)이며 칠살(편관)로 읽습니다.", "b.year.stem", None),
            ("둘째의 연간은 壬입니다. 이 자리의 십성은 편 관입니다.", "b.year.stem", None),
            ("첫째의 일지와 둘째의 연지입니다. 이 두 자리에는 육 합이 있습니다.",
             "pair.육합.a.day.b.year", None),
            ("두 사람의 말투와는 상관이 없습니다. 생활 속에서 찾아볼 만한 차이입니다.",
             "a.day.stem", None),
            ("첫째의 연간은 칠살에 해당합니다.", "b.year.stem", "scoped_fact_mismatch"),
            ("둘째의 월간은 칠살에 해당합니다.", "b.year.stem", "scoped_fact_mismatch"),
            ("둘째의 연간은 병화입니다.", "b.year.stem", "pillar_symbol_mismatch"),
            ("둘째의 연간은 임(丙)입니다.", "b.year.stem", "pillar_symbol_mismatch"),
            ("둘째의 배우자궁은 사(巳)입니다.", "a.palace", "pillar_symbol_mismatch"),
            ("첫째의 시주는 계사입니다.", "a.day.stem", "unresolved_pillar_claim"),
            ("둘째의 시주는 확인되지 않았습니다.", "b.coverage", None),
            ("둘째의 시주는 확인되지 않았으므로, 이 설명은 확인된 세 기둥을 바탕으로 한 해석입니다.",
             "b.coverage", None),
            ("둘째의 시주는 확인되지 않았으므로 추정한 시주는 계사입니다.",
             "b.coverage", "unresolved_pillar_claim"),
            ("둘째의 시주는 미상입니다. 둘째의 시지는 巳입니다.",
             "b.coverage", "unresolved_pillar_claim"),
            ("둘째의 일지와 첫째의 연지입니다. 이 두 자리에는 육합이 있습니다.",
             "pair.육합.a.day.b.year", "scoped_fact_mismatch"),
            ("둘째에게 첫째의 일간은 정재입니다.", "pair.a.reads.b", "scoped_fact_mismatch"),
        ]
        for claim, ref, rule in cases:
            with self.subTest(claim=claim):
                sample = json.loads((ROOT / "rs_gpt_mock.json").read_text(encoding="utf-8"))["sol-61"]
                first, second = sample["chapters"][0]["paragraphs"]
                first.update(text=claim + " 가까운 관계를 읽을 때 참고하는 자리입니다.",
                             evidence_ids=["a.day.stem"])
                second.update(text="이 문단의 근거는 앞 문장에서 살핀 기둥과 관련이 있습니다.",
                              evidence_ids=[ref])
                if rule:
                    with self.assertRaises(ExperimentError) as error:
                        validate(sample, facts)
                    self.assertEqual(error.exception.diagnostic["rule"], rule)
                else:
                    self.assertEqual(validate(sample, facts)["paragraphs"], 7)

    @patch("rs_gpt_server.run_report")
    def test_editorial_sample_requires_admin_and_stays_offline(self, report):
        address = self.origin + EDITORIAL_SAMPLE_API
        with patch.dict("os.environ", {"RS_GPT_ADMIN_TOKEN": self.token, "RS_GPT_LIVE": "0"}):
            with self.assertRaises(HTTPError) as denied:
                urlopen(address, timeout=5)
            self.assertEqual(denied.exception.code, 403)
            with urlopen(Request(address, headers={"Authorization": f"Bearer {self.token}"}),
                         timeout=5) as response:
                self.assertEqual(response.headers["Cache-Control"], "no-store")
                sample = json.load(response)
        report.assert_not_called()
        self.assertEqual(sample["names"], {"a": "윤하", "b": "도현"})
        self.assertEqual(sample["charts"]["a"]["pillars"]["hour"], "癸巳")
        self.assertIsNone(sample["charts"]["b"]["pillars"]["hour"])
        self.assertEqual(sample["symbols"]["丙"]["element_name"], "화")
        self.assertEqual(len(sample["chapters"]), 3)
        lengths = [sum(len(p.get("text", "")) for p in chapter["paragraphs"])
                   for chapter in sample["chapters"]]
        self.assertEqual(lengths[1], max(lengths))

    @patch("rs_gpt.request_openai")
    def test_failed_manuscript_is_only_available_to_admin(self, provider):
        sample = json.loads((ROOT / "rs_gpt_mock.json").read_text(encoding="utf-8"))["sol-62"]
        sample["chapters"][0]["title"] = "1장. 처음 만난 두 사람"
        sample["chapters"][0]["paragraphs"][0] = {
            "text": "민준님의 일간과 연주에는 육충이 있습니다. <script>원고표식</script>",
            "evidence_ids": ["a.day.stem"],
        }
        original = json.dumps(sample, ensure_ascii=False, indent=2)
        provider.return_value = {"status": "completed", "output": [{"type": "message",
                                 "content": [{"type": "output_text", "text": original}]}]}
        config = {"RS_GPT_LIVE": "1", "OPENAI_API_KEY": "mock-transport-key",
                  "RS_GPT_ADMIN_TOKEN": self.token, "RS_GPT_LOCAL_LEDGER": "test-only"}
        address = self.origin + DIAGNOSTIC_API
        authorized = Request(address, headers={"Authorization": f"Bearer {self.token}"})
        diagnostic = GroundingDiagnostic()
        with patch.dict("os.environ", config), patch("rs_gpt_server.GROUNDING_DIAGNOSTIC", diagnostic):
            with self.assertLogs("rs_gpt", "INFO") as logs, self.assertRaises(HTTPError) as error:
                self.post_admin(self.token)
            self.addCleanup(diagnostic.timer.cancel)
            self.assertEqual(error.exception.code, 502)
            self.assertEqual(set(json.load(error.exception)), {"error", "code", "metrics"})
            log = "\n".join(logs.output)
            self.assertIn("scoped_fact_mismatch", log)
            for private in ("민준", "1992-03-18", "원고표식", "육충", "a.day.stem"):
                self.assertNotIn(private, log)
            for headers in ({}, {"Authorization": "Bearer incorrect"}):
                with self.assertRaises(HTTPError) as denied:
                    urlopen(Request(address, headers=headers), timeout=5)
                self.assertEqual(denied.exception.code, 403)
                self.assertNotIn("original", json.load(denied.exception))
            with patch.dict("os.environ", {"RS_GPT_LIVE": "0"}):
                with urlopen(authorized, timeout=5) as response:
                    self.assertEqual(response.headers["Cache-Control"], "no-store")
                    self.assertEqual(response.headers.get_content_type(), "application/json")
                    report = json.load(response)
            self.assertEqual(report["original"], original)
            self.assertEqual(report["failure"]["excerpt"], "민준님의 일간과 연주에는 육충이 있습니다")
            self.assertEqual(report["failure"]["category"], "evidence")
            self.assertEqual(report["failure"]["evidence_ids"], ["a.day.stem"])
            self.assertIn("a.day.stem", report["reference"]["facts"])
            self.assertNotIn("1992-03-18", json.dumps(report))
            with patch("rs_gpt_server.time.monotonic", return_value=diagnostic.deadline):
                with self.assertRaises(HTTPError) as expired:
                    urlopen(authorized, timeout=5)
                self.assertEqual(expired.exception.code, 404)
        provider.assert_called_once()

    def test_diagnostic_timer_deletes_without_a_read(self):
        diagnostic = GroundingDiagnostic()
        with patch("rs_gpt_server.DIAGNOSTIC_TTL", 0.02):
            diagnostic.capture({"original": "first"})
            diagnostic.capture({"original": "last"})
            timer = diagnostic.timer
        if timer is not None:
            timer.join(timeout=1)
        self.assertIsNone(diagnostic.record)

    @patch("rs_gpt.request_openai", return_value={"status": "incomplete"})
    def test_reports_incomplete_without_returning_prose(self, request):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "mock-transport-key"}):
            with self.assertRaises(ExperimentError) as error:
                run_report("sol-61", "live", live_enabled=True)
        self.assertEqual(error.exception.code, "incomplete")
        self.assertIsInstance(error.exception.metrics["latency_ms"], int)

