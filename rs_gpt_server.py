"""Run the comparison in its own process, independently of the product server."""
import hmac
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from rs_gpt import ROOT, PROFILES, ExperimentError, fixed_case, run_report
from rs_gpt_budget import render_budget

LOOPBACK = ("127.0.0.1", "localhost")
RENDER_SERVICE_ID = "srv-dc23purl550s7381llg0"


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

    def do_GET(self):
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

