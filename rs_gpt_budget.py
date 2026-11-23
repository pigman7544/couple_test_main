"""Persistent admission control for the Render experiment."""
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
import time

from rs_gpt import ExperimentError

MONTHLY_MICRO_USD = 7_000_000
MONTHLY_CALLS = 3
COOLDOWN_SECONDS = 300
LOCK_ID = 376118


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


@contextmanager
def render_budget(reservation):
    # Load the database dependency only for Render live requests.
    import psycopg

    try:
        with psycopg.connect(os.environ["RS_GPT_BUDGET_DSN"], connect_timeout=5,
                             options="-c statement_timeout=5000") as db:
            if not db.execute("SELECT pg_try_advisory_lock(%s)", (LOCK_ID,)).fetchone()[0]:
                raise ExperimentError("busy", "다른 원고를 작성 중입니다.", 429)
            db.execute("""
                CREATE TABLE IF NOT EXISTS rs_gpt_reservations (
                    reserved_at timestamptz NOT NULL,
                    micro_usd integer NOT NULL CHECK (micro_usd > 0)
                )
            """)
            now = datetime.now(timezone.utc)
            month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            count, spent, last = db.execute("""
                SELECT COUNT(*) FILTER (WHERE reserved_at >= %s),
                       COALESCE(SUM(micro_usd) FILTER (WHERE reserved_at >= %s), 0),
                       MAX(reserved_at)
                FROM rs_gpt_reservations
            """, (month, month)).fetchone()
            check_budget(count, spent, (now - last).total_seconds() if last else float("inf"),
                         reservation)
            db.execute("INSERT INTO rs_gpt_reservations VALUES (%s, %s)", (now, reservation))
            # Commit before the upstream call. Uncertain outcomes retain their reservation.
            db.commit()
            yield
    except psycopg.Error:
        raise ExperimentError("budget_store", "호출 한도를 확인할 수 없습니다.", 503) from None
