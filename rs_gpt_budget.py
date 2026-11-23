"""Persistent admission control for the Render experiment."""
from contextlib import contextmanager
from datetime import datetime, timezone
import os

from rs_gpt import ExperimentError

MONTHLY_MICRO_USD = 7_000_000
LOCK_ID = 376118


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
            spent, last = db.execute("""
                SELECT COALESCE(SUM(micro_usd) FILTER (WHERE reserved_at >= %s), 0),
                       MAX(reserved_at)
                FROM rs_gpt_reservations
            """, (month,)).fetchone()
            if last and (now - last).total_seconds() < 20:
                raise ExperimentError("cooldown", "요청 간격은 최소 20초입니다.", 429)
            if spent + reservation > MONTHLY_MICRO_USD:
                raise ExperimentError("budget", "이달 실험 호출 예산을 모두 예약했습니다.", 429)
            db.execute("INSERT INTO rs_gpt_reservations VALUES (%s, %s)", (now, reservation))
            # Commit before the upstream call. Uncertain outcomes retain their reservation.
            db.commit()
            yield
    except psycopg.Error:
        raise ExperimentError("budget_store", "호출 한도를 확인할 수 없습니다.", 503) from None
