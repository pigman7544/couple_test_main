"""Run the comparison in its own process, independently of the product server."""
import hashlib
import hmac
import json
import logging
import os
import secrets
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from rs_gpt import ROOT, PROFILES, ExperimentError, fixed_case, run_report
from rs_gpt_budget import render_budget
from rs_gpt import extract_report, request_openai, usage_metrics, validate

LOOPBACK = ("127.0.0.1", "localhost")
RENDER_SERVICE_ID = "srv-dc23purl550s7381llg0"

REVIEW_PATH = "/api/rs-gpt-admin-review"
REVIEW_HASH = "156a3b9e214d953a9071710e4be208282f47236e41652c4c5c22e50a9853488f"
REVIEW_EXPIRES_AT = 1795444959
REVIEW_PROFILES = ("sol-61", "sol-62")
REVIEW_NONCE = secrets.token_hex(32)
REVIEW_LOCK = threading.Lock()
REVIEW_STATE = {"started": False, "done": False, "results": []}


@contextmanager
def review_budget(reservation):
    if not 0 < reservation <= 2.155001:
        raise ExperimentError("budget", "검증 호출의 비용 상한을 초과했습니다.")
    yield


def review_model(profile_id):
    profile = PROFILES[profile_id]
    result = {"profile": profile_id, "model": profile["model"], "effort": profile["effort"]}
    started = time.perf_counter()
    try:
        payload, _ = fixed_case()
        response = request_openai(payload, profile, os.environ["OPENAI_API_KEY"], review_budget)
        result["response_model"] = response.get("model")
        result["usage"] = usage_metrics(response.get("usage"), profile)
        result["provider_status"] = response.get("status")
        report = extract_report(response)
        result["report"] = report
        try:
            result["audit"] = validate(report, payload["facts"])
        except ExperimentError as exc:
            result["audit_error"] = exc.code
    except ExperimentError as exc:
        result["error"] = exc.code
    except Exception:
        result["error"] = "internal"
    result["latency_ms"] = round((time.perf_counter() - started) * 1000)
    logging.getLogger("rs_gpt").info("%s", json.dumps({
        "event": "admin_review", "profile": profile_id,
        "status": result.get("error", result.get("audit_error", "ok")),
        "latency_ms": result["latency_ms"], "usage": result.get("usage"),
    }))
    return result


def run_review():
    try:
        for index, profile in enumerate(REVIEW_PROFILES):
            if index:
                time.sleep(20)
            if time.time() >= REVIEW_EXPIRES_AT:
                break
            result = review_model(profile)
            with REVIEW_LOCK:
                REVIEW_STATE["results"].append(result)
    finally:
        with REVIEW_LOCK:
            REVIEW_STATE["done"] = True


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Do not record client IP, request URL, or user agent.
        pass

    def write_response(self, status, raw, content_type):
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(raw)

    def json_response(self, status, body):
        self.write_response(status, json.dumps(body, ensure_ascii=False).encode(), "application/json")

    def live_enabled(self):
        if os.environ.get("RS_GPT_LIVE") != "1" or not os.environ.get("OPENAI_API_KEY"):
            return False
        if os.environ.get("RENDER") != "true":
            return self.server.server_address[0] in LOOPBACK
        return (os.environ.get("RENDER_SERVICE_ID") == RENDER_SERVICE_ID
                and bool(os.environ.get("RS_GPT_BUDGET_DSN"))
                and len(os.environ.get("RS_GPT_ADMIN_TOKEN", "")) >= 32)

    def admin_authorized(self):
        secret = os.environ.get("RS_GPT_ADMIN_TOKEN", "")
        actual = self.headers.get("Authorization", "").encode("utf-8")
        return len(secret) >= 32 and hmac.compare_digest(actual, f"Bearer {secret}".encode())

    def review_authorized(self):
        auth = self.headers.get("Authorization", "")
        return (
            os.environ.get("RENDER") == "true"
            and os.environ.get("RENDER_SERVICE_ID") == RENDER_SERVICE_ID
            and time.time() < REVIEW_EXPIRES_AT
            and len(auth) == 71
            and auth.startswith("Bearer ")
            and hmac.compare_digest(hashlib.sha256(auth[7:].encode()).hexdigest(), REVIEW_HASH)
        )

    def handle_review(self):
        if not self.review_authorized():
            self.json_response(403, {"code": "forbidden"})
            return
        if self.command == "GET":
            with REVIEW_LOCK:
                state = {**REVIEW_STATE, "results": list(REVIEW_STATE["results"])}
            self.json_response(200, {"nonce": REVIEW_NONCE, **state})
            return
        if self.headers.get("X-Review-Nonce") != REVIEW_NONCE:
            self.json_response(409, {"code": "wrong_instance"})
            return
        if not os.environ.get("OPENAI_API_KEY"):
            self.json_response(503, {"code": "key_missing"})
            return
        with REVIEW_LOCK:
            if REVIEW_STATE["started"]:
                self.json_response(409, {"code": "already_started"})
                return
            REVIEW_STATE["started"] = True
            threading.Thread(target=run_review, daemon=True).start()
        self.json_response(202, {"code": "started"})

    def do_GET(self):
        if self.path == REVIEW_PATH:
            self.handle_review()
            return
        if self.path in ("/", "/rs-gpt"):
            self.write_response(200, (ROOT / "rs_gpt.html").read_bytes(), "text/html")
        elif self.path == "/health":
            self.write_response(200, b"OK", "text/plain")
        elif self.path == "/api/rs-gpt":
            facts, baseline = fixed_case()
            self.json_response(200, {**facts, "baseline": baseline,
                                     "profiles": PROFILES, "live_enabled": (
                                         self.live_enabled() and (
                                             os.environ.get("RENDER") != "true"
                                             or self.admin_authorized()
                                         )
                                     )})
        else:
            self.json_response(404, {"error": "페이지를 찾을 수 없습니다."})

    def do_POST(self):
        if self.path == REVIEW_PATH:
            self.handle_review()
            return
        if self.path != "/api/rs-gpt":
            self.json_response(404, {"error": "페이지를 찾을 수 없습니다."})
            return
        try:
            if self.headers.get_content_type() != "application/json":
                raise ValueError
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 512:
                raise ValueError
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict) or set(data) != {"profile", "mode"}:
                raise ValueError
            enabled = self.live_enabled()
            on_render = os.environ.get("RENDER") == "true"
            if data["mode"] == "live" and on_render and not self.admin_authorized():
                raise ExperimentError("forbidden", "관리자 인증이 필요합니다.", 403)
            result = run_report(data["profile"], data["mode"], enabled,
                                render_budget if on_render else None)
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
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    host = os.environ.get("RS_GPT_HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8766"))
    with ThreadingHTTPServer((host, port), Handler) as server:
        print(f"RS GPT review on {host}:{port}", flush=True)
        server.serve_forever()

