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
COOLDOWN_SECONDS = 300
LOCK_ID = 376118
RUNTIME_ROLE = "rs_gpt_runtime"
LOGGER = logging.getLogger(__name__)


def check_budget(count, spent, elapsed, reservation):
    if elapsed < COOLDOWN_SECONDS:
        raise ExperimentError("cooldown", "실험 요청 간격은 최소 5분입니다.", 429)
    if count >= MONTHLY_CALLS or spent + reservation > MONTHLY_MICRO_USD:
        raise ExperimentError("budget", "이달 실험 호출 한도에 도달했습니다.", 429)


def init_local_budget(path):
    # Explicit initialization prevents accidental quota reset on a missing file.
    filename = Path(path).resolve()
    with filename.open("xb"):
        pass
    with closing(sqlite3.connect(filename)) as db, db:
        db.execute("CREATE TABLE reservations (reserved_at INTEGER, micro_usd INTEGER)")


@contextmanager
def local_budget(reservation):
    try:
        path = Path(os.environ["RS_GPT_LOCAL_LEDGER"]).resolve().as_uri()
        with closing(sqlite3.connect(path + "?mode=rw", uri=True, timeout=5)) as db, db:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            now = int(time.time())
            month = int(datetime.fromtimestamp(now, timezone.utc).replace(
                day=1, hour=0, minute=0, second=0).timestamp())
            count, spent = db.execute(
                "SELECT COUNT(*), COALESCE(SUM(micro_usd), 0) FROM reservations "
                "WHERE reserved_at >= ?", (month,)).fetchone()
            last = db.execute("SELECT MAX(reserved_at) FROM reservations").fetchone()[0]
            check_budget(count, spent, now - (last or 0), reservation)
            db.execute("INSERT INTO reservations VALUES (?, ?)", (now, reservation))
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
    return psycopg.connect(
        host=host, hostaddr="", dbname=config.get("dbname", "neondb"),
        user=RUNTIME_ROLE, password=config.get("password", ""), port=5432,
        sslmode="verify-full", sslrootcert="system", channel_binding="require",
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
                stage = "insert"
                db.execute("""
                    INSERT INTO rs_gpt_ledger.reservations (reserved_at, micro_usd)
                    VALUES (clock_timestamp(), 1)
                """)
                stage = "rollback"
            return {"reservations": count, "reserved_micro_usd": reserved}
    except psycopg.Error as error:
        LOGGER.warning("RS GPT ledger check failed: stage=%s error=%s sqlstate=%s",
                       stage, type(error).__name__, error.sqlstate or "none")
        raise ExperimentError("budget_store", "호출 원장을 확인할 수 없습니다.", 503) from None


@contextmanager
def render_budget(reservation):
    import psycopg

    try:
        with connect_render_ledger() as db:
            if not db.execute("SELECT pg_try_advisory_lock(%s)", (LOCK_ID,)).fetchone()[0]:
                raise ExperimentError("busy", "다른 원고를 작성 중입니다.", 429)
            now = db.execute("SELECT clock_timestamp()").fetchone()[0].astimezone(timezone.utc)
            month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            count, spent, last = db.execute("""
                SELECT COUNT(*) FILTER (WHERE reserved_at >= %s),
                       COALESCE(SUM(micro_usd) FILTER (WHERE reserved_at >= %s), 0),
                       MAX(reserved_at)
                FROM rs_gpt_ledger.reservations
            """, (month, month)).fetchone()
            check_budget(count, spent, (now - last).total_seconds() if last else float("inf"),
                         reservation)
            db.execute(
                "INSERT INTO rs_gpt_ledger.reservations (reserved_at, micro_usd) VALUES (%s, %s)",
                (now, reservation),
            )
            # Commit before the upstream call. Uncertain outcomes retain their reservation.
            db.commit()
            yield
    except psycopg.Error:
        raise ExperimentError("budget_store", "호출 한도를 확인할 수 없습니다.", 503) from None
