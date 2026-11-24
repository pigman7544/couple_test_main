"""Run the comparison in its own process, independently of the product server."""
import hmac
import json
import logging
import os
import re
import sys
from datetime import date
from unicodedata import category, normalize
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from rs_gpt import ROOT, PROFILES, ExperimentError, birth_payload, fixed_case, run_report
from rs_gpt_budget import init_local_budget, local_budget, render_budget, verify_render_ledger
from server import ART_PATHS, match_inputs

LOOPBACK = ("127.0.0.1", "localhost")
RENDER_SERVICE_ID = "srv-dc23purl550s7381llg0"
ADMIN_PATH = "/rs-gpt/admin"
ADMIN_API = "/api/rs-gpt/admin"
LEDGER_API = "/api/rs-gpt/admin/ledger"


def admin_token():
    # The browser trims surrounding whitespace before sending the bearer token.
    return os.environ.get("RS_GPT_ADMIN_TOKEN", "").strip()


def parse_birth(data):
    if not isinstance(data, dict) or "date" not in data or set(data) - {"date", "time", "gender"}:
        raise ValueError
    birthday, clock, gender = data["date"], data.get("time"), data.get("gender")
    if (not isinstance(birthday, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", birthday)
            or gender not in (None, "", "male", "female", "other")):
        raise ValueError
    birthday = date.fromisoformat(birthday)
    if not 1000 <= birthday.year <= 2050:
        raise ValueError
    if clock is None or clock == "":
        hour, minute = None, 0
    elif isinstance(clock, str) and re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", clock):
        hour, minute = map(int, clock.split(":"))
    else:
        raise ValueError
    return dict(year=birthday.year, month=birthday.month, day=birthday.day,
                hour=hour, minute=minute), gender


def parse_person(data):
    if not isinstance(data, dict) or not isinstance(data.get("name"), str):
        raise ValueError
    name = normalize("NFC", data["name"]).strip()
    if not 1 <= len(name) <= 32 or not any(char.isalpha() for char in name) or any(
        category(char)[0] not in "LM" and char not in " -·'’" for char in name
    ):
        raise ValueError
    birth, gender = parse_birth({key: value for key, value in data.items() if key != "name"})
    return birth, gender, name


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Do not record client IP, request URL, or user agent.
        pass

    def write_response(self, status, raw, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type if content_type == "image/png"
                         else f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; script-src 'unsafe-inline'; "
                         "style-src 'unsafe-inline'; img-src 'self'; connect-src 'self'; form-action 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def json_response(self, status, body):
        self.write_response(status, json.dumps(body, ensure_ascii=False).encode(), "application/json")

    def live_enabled(self):
        if (os.environ.get("RS_GPT_LIVE") != "1" or not os.environ.get("OPENAI_API_KEY")
                or len(admin_token()) < 32):
            return False
        if os.environ.get("RENDER") != "true":
            return (self.server.server_address[0] in LOOPBACK
                    and bool(os.environ.get("RS_GPT_LOCAL_LEDGER")))
        return (os.environ.get("RENDER_SERVICE_ID") == RENDER_SERVICE_ID
                and bool(os.environ.get("RS_GPT_BUDGET_DSN")))

    def admin_authorized(self):
        secret = admin_token()
        actual = self.headers.get("Authorization", "").encode("utf-8")
        return len(secret) >= 32 and hmac.compare_digest(actual, f"Bearer {secret}".encode())

    def do_GET(self):
        if self.path in ("/", "/rs-gpt"):
            self.write_response(200, (ROOT / "rs_gpt.html").read_bytes(), "text/html")
        elif self.path == ADMIN_PATH:
            self.write_response(200, (ROOT / "rs_gpt_admin.html").read_bytes(), "text/html")
        elif self.path in ART_PATHS and (asset := ROOT / self.path.lstrip("/")).is_file():
            self.write_response(200, asset.read_bytes(), "image/png")
        elif self.path == ADMIN_API:
            if not self.admin_authorized():
                self.json_response(403, {"error": "관리자 인증이 필요합니다."})
            else:
                self.json_response(200, {
                    "live_enabled": self.live_enabled(),
                    "ledger_check": os.environ.get("RENDER_SERVICE_ID") == RENDER_SERVICE_ID,
                })
        elif self.path == LEDGER_API:
            if not self.admin_authorized():
                self.json_response(403, {"error": "관리자 인증이 필요합니다."})
            elif os.environ.get("RENDER_SERVICE_ID") != RENDER_SERVICE_ID:
                self.json_response(404, {"error": "페이지를 찾을 수 없습니다."})
            else:
                try:
                    self.json_response(200, verify_render_ledger())
                except ExperimentError as exc:
                    self.json_response(exc.status, {"error": str(exc), "code": exc.code})
        elif self.path == "/health":
            self.write_response(200, b"OK", "text/plain")
        elif self.path == "/api/rs-gpt":
            facts, baseline = fixed_case()
            self.json_response(200, {**facts, "baseline": baseline,
                                     "profiles": PROFILES, "live_enabled": False})
        else:
            self.json_response(404, {"error": "페이지를 찾을 수 없습니다."})

    def do_POST(self):
        if self.path not in ("/api/rs-gpt", ADMIN_API):
            self.json_response(404, {"error": "페이지를 찾을 수 없습니다."})
            return
        try:
            if self.path == ADMIN_API and not self.admin_authorized():
                raise ExperimentError("forbidden", "관리자 인증이 필요합니다.", 403)
            if self.headers.get_content_type() != "application/json":
                raise ValueError
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 1024:
                raise ValueError
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError
            if self.path == ADMIN_API:
                if set(data) - {"a", "b", "mode"} or not {"a", "b"} <= set(data):
                    raise ValueError
                mode = data.get("mode", "live")
                if mode not in ("live", "preview"):
                    raise ValueError
                if mode == "live" and not self.live_enabled():
                    raise ExperimentError("disabled", "실시간 집필 설정이 준비되지 않았습니다.", 503)
                a, gender_a, name_a = parse_person(data["a"])
                b, gender_b, name_b = parse_person(data["b"])
                payload = birth_payload(a, b, {"a": gender_a, "b": gender_b})
                payload["names"] = {"a": name_a, "b": name_b}
                _, _, _, _, _, ranked, art = match_inputs(data)
                couple = ranked[0][2]
                payload["couple"] = {key: couple[key] for key in ("id", "name", "work")}
                result = {**payload, "art": art}
                if mode == "live":
                    budget = render_budget if os.environ.get("RENDER") == "true" else local_budget
                    result.update(run_report("sol-62", "live", True, budget, payload))
            else:
                if set(data) != {"profile", "mode"}:
                    raise ValueError
                if data["mode"] != "mock":
                    raise ExperimentError("forbidden", "실호출은 관리자 화면에서만 가능합니다.", 403)
                result = run_report(data["profile"], "mock")
        except ExperimentError as exc:
            self.json_response(exc.status, {"error": str(exc), "code": exc.code,
                                            "metrics": getattr(exc, "metrics", None)})
        except (ValueError, UnicodeError):
            self.json_response(400, {"error": "요청 형식을 확인해 주세요."})
        except Exception:
            self.json_response(500, {"error": "검토 서버에서 원고를 처리하지 못했습니다."})
        else:
            self.json_response(200, result)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--init-ledger":
        init_local_budget(sys.argv[2])
        raise SystemExit
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if len(admin_token()) < 32:
        logging.warning("RS GPT administrator authentication is unavailable: configure a token of at least 32 characters.")
    host = "0.0.0.0" if os.environ.get("RENDER") == "true" else "127.0.0.1"
    port = int(os.environ.get("PORT", "8766"))
    with ThreadingHTTPServer((host, port), Handler) as server:
        print(f"RS GPT review on {host}:{port}", flush=True)
        server.serve_forever()

