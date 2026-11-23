-- Run once as the existing database owner on the experiment Neon database.
-- Set the runtime role's generated password separately in the Neon console.
BEGIN;

-- A pre-existing ledger must be migrated explicitly to preserve reservations.
DO $$
BEGIN
    IF to_regclass('public.rs_gpt_reservations') IS NOT NULL THEN
        RAISE EXCEPTION 'Legacy RS GPT ledger exists; migrate reservations before proceeding';
    END IF;
END
$$;

CREATE ROLE rs_gpt_runtime LOGIN NOINHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE SCHEMA rs_gpt_ledger;
REVOKE ALL ON SCHEMA rs_gpt_ledger FROM PUBLIC;

CREATE TABLE rs_gpt_ledger.reservations (
    reserved_at timestamptz NOT NULL,
    micro_usd integer NOT NULL CHECK (micro_usd > 0)
);

REVOKE ALL ON TABLE rs_gpt_ledger.reservations FROM PUBLIC;
GRANT USAGE ON SCHEMA rs_gpt_ledger TO rs_gpt_runtime;
GRANT SELECT, INSERT ON TABLE rs_gpt_ledger.reservations TO rs_gpt_runtime;

COMMIT;
