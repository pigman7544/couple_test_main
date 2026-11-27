"""Persistent admission control for the Render experiment."""
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import re
import sqlite3
import time

from rs_gpt import ExperimentError

MONTHLY_MICRO_USD = 7_000_000
MONTHLY_CALLS = 3
RENDER_SERVICE_ID = "srv-dc23purl550s7381llg0"
COOLDOWN_SECONDS = 300
LOCK_ID = 376118
RUNTIME_ROLE = "rs_gpt_runtime"
LOGGER = logging.getLogger(__name__)


def monthly_call_limit():
    if (os.environ.get("RENDER") == "true"
            and os.environ.get("RENDER_SERVICE_ID") == RENDER_SERVICE_ID):
        configured = os.environ.get("RS_GPT_MONTHLY_CALLS")
        november_2026 = datetime(2026, 11, 1, tzinfo=timezone.utc)
        if configured == "9" and month_start(datetime.now(timezone.utc)) == november_2026:
            return 9
        if configured in ("5", "9"):
            return 5
    return MONTHLY_CALLS


def month_start(now):
    # Keep the existing UTC rollover, which is 09:00 in Korea.
    return now.astimezone(timezone.utc).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)


def render_usage(db):
    now = db.execute("SELECT clock_timestamp()").fetchone()[0]
    month = month_start(now)
    count, spent, last = db.execute("""
        SELECT COUNT(*) FILTER (WHERE reserved_at >= %s),
               COALESCE(SUM(micro_usd) FILTER (WHERE reserved_at >= %s), 0),
               MAX(reserved_at)
        FROM rs_gpt_ledger.reservations
    """, (month, month)).fetchone()
    return now, count, spent, last


def check_budget(count, spent, elapsed, reservation, calls=1):
    if elapsed < COOLDOWN_SECONDS:
        raise ExperimentError("cooldown", "실험 요청 간격은 최소 5분입니다.", 429)
    if count + calls > monthly_call_limit() or spent + reservation * calls > MONTHLY_MICRO_USD:
        raise ExperimentError("budget", "이달 실험 호출 한도에 도달했습니다.", 429)


def init_local_budget(path):
    # Explicit initialization prevents accidental quota reset on a missing file.
    filename = Path(path).resolve()
    with filename.open("xb"):
        pass
    with closing(sqlite3.connect(filename)) as db, db:
        db.execute("CREATE TABLE reservations (reserved_at INTEGER, micro_usd INTEGER)")


@contextmanager
def local_budget(reservation, calls=1):
    try:
        path = Path(os.environ["RS_GPT_LOCAL_LEDGER"]).resolve().as_uri()
        with closing(sqlite3.connect(path + "?mode=rw", uri=True, timeout=5)) as db, db:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            now = int(time.time())
            month = int(month_start(datetime.fromtimestamp(now, timezone.utc)).timestamp())
            count, spent = db.execute(
                "SELECT COUNT(*), COALESCE(SUM(micro_usd), 0) FROM reservations "
                "WHERE reserved_at >= ?", (month,)).fetchone()
            last = db.execute("SELECT MAX(reserved_at) FROM reservations").fetchone()[0]
            check_budget(count, spent, now - (last or 0), reservation, calls)
            db.executemany("INSERT INTO reservations VALUES (?, ?)", [(now, reservation)] * calls)
    except (sqlite3.Error, OSError, KeyError):
        raise ExperimentError("budget_store", "호출 한도를 확인할 수 없습니다.", 503) from None
    yield


def connect_render_ledger():
    import psycopg
    from psycopg.conninfo import conninfo_to_dict

    config = conninfo_to_dict(os.environ.get("RS_GPT_BUDGET_DSN", ""))
    host = config.get("host", "")
    if (not re.fullmatch(r"ep-[a-z0-9-]+\.[a-z0-9.-]+\.neon\.tech", host)
            or host.split(".")[0].endswith("-pooler")
            or config.get("hostaddr") or config.get("service")
            or config.get("user") != RUNTIME_ROLE):
        raise ExperimentError("budget_store", "Neon 직접 연결 설정을 확인해 주세요.", 503)
    # The bundled libpq may use a different OpenSSL trust path on Render.
    ca_bundle = Path("/etc/ssl/certs/ca-certificates.crt")
    root_cert = str(ca_bundle) if ca_bundle.is_file() else "system"
    return psycopg.connect(
        host=host, hostaddr="", dbname=config.get("dbname", "neondb"),
        user=RUNTIME_ROLE, password=config.get("password", ""), port=5432,
        sslmode="verify-full", sslrootcert=root_cert, channel_binding="require",
        connect_timeout=5, options="-c statement_timeout=5000",
    )


def verify_render_ledger():
    import psycopg

    stage = "connect"
    try:
        with connect_render_ledger() as db:
            stage = "lock"
            if not db.execute("SELECT pg_try_advisory_lock(%s)", (LOCK_ID,)).fetchone()[0]:
                raise ExperimentError("busy", "다른 원고를 작성 중입니다.", 429)
            db.commit()
            stage = "second_connection"
            with connect_render_ledger() as other:
                stage = "lock_isolation"
                if other.execute("SELECT pg_try_advisory_lock(%s)", (LOCK_ID,)).fetchone()[0]:
                    raise ExperimentError("budget_store", "원장 잠금을 확인할 수 없습니다.", 503)
            stage = "role_privileges"
            with db.transaction(force_rollback=True):
                can_modify = db.execute("""
                    SELECT has_schema_privilege('rs_gpt_ledger', 'CREATE')
                        OR has_table_privilege('rs_gpt_ledger.reservations', 'UPDATE, DELETE, TRUNCATE')
                        OR pg_has_role('neon_superuser', 'MEMBER')
                """).fetchone()[0]
                if can_modify:
                    raise ExperimentError("budget_store", "원장 접속 권한을 확인해 주세요.", 503)
                stage = "select"
                count, reserved = db.execute("""
                    SELECT COUNT(*), COALESCE(SUM(micro_usd), 0)
                    FROM rs_gpt_ledger.reservations
                """).fetchone()
                _, month_count, month_reserved, _ = render_usage(db)
                stage = "insert"
                db.execute("""
                    INSERT INTO rs_gpt_ledger.reservations (reserved_at, micro_usd)
                    VALUES (clock_timestamp(), 1)
                """)
                stage = "rollback"
            limit = monthly_call_limit()
            return {
                "reservations": count,
                "reserved_micro_usd": reserved,
                "monthly_reservations": month_count,
                "monthly_reserved_micro_usd": month_reserved,
                "monthly_call_limit": limit,
                "monthly_calls_remaining": max(0, limit - month_count),
                "monthly_budget_micro_usd": MONTHLY_MICRO_USD,
            }
    except psycopg.Error as error:
        LOGGER.warning("RS GPT ledger check failed: stage=%s error=%s sqlstate=%s",
                       stage, type(error).__name__, error.sqlstate or "none")
        raise ExperimentError("budget_store", "호출 원장을 확인할 수 없습니다.", 503) from None


@contextmanager
def render_budget(reservation, calls=1):
    import psycopg

    try:
        with connect_render_ledger() as db:
            if not db.execute("SELECT pg_try_advisory_lock(%s)", (LOCK_ID,)).fetchone()[0]:
                raise ExperimentError("busy", "다른 원고를 작성 중입니다.", 429)
            now, count, spent, last = render_usage(db)
            check_budget(count, spent, (now - last).total_seconds() if last else float("inf"),
                         reservation, calls)
            with db.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO rs_gpt_ledger.reservations (reserved_at, micro_usd) VALUES (%s, %s)",
                    [(now, reservation)] * calls,
                )
            # Commit before the upstream call. Uncertain outcomes retain their reservation.
            db.commit()
            yield
    except psycopg.Error:
        raise ExperimentError("budget_store", "호출 한도를 확인할 수 없습니다.", 503) from None
