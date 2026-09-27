\# Project State



\## Pipeline

CSV → extract → transform → load → Postgres



\## What works

\- `src/extract.py` — reads raw CSV, logs rows + file size

\- `src/transform.py` — EMPTY (Day 4)

\- `src/load.py` — EMPTY (Day 5)

\- `main.py` — orchestrates extract + transform (inline) + load (inline)

\- Tests: `test/test\_extract.py` — 2 passing

\- Postgres running in Docker (`cambodia\_fx\_db` on port 5432)

\- Schema: `sql/01\_create\_schema.sql` runs on first container start



\## How to start the DB

docker compose up -d

docker compose ps          # wait for "healthy"



\## How to run the pipeline

python main.py



\## How to run tests

pytest test/ -v



\## Connect to DB manually

docker compose exec db psql -U exchange\_user -d exchange\_db



\## Current row count

SELECT COUNT(\*) FROM exchange\_rates;   -- expected: 7531



\## Day 4 task

Move transform() from main.py → src/transform.py, add tests



\## Gotchas learned

\- Postgres 18 image mounts at /var/lib/postgresql (not /data)

\- Init SQL only reruns on empty volume: docker compose down -v

\- pytest needs pythonpath = . in pytest.ini

\- Code Runner temp file strips imports — use `python main.py` instead


======== Pandas Syntax ==============

pd.read_csv("path") — read a file

df.head() — look at the top

df.info() — see column types and nulls

df.columns — list column names

df["col"] — pick a column

pd.to_datetime(...) — parse dates

pd.to_numeric(...) — parse numbers

df.dropna(...) — remove null rows

df.drop_duplicates(...) — remove dupes

df.to_csv("path") — save to file

logging.info(...) — log a message

def function_name(args): — define a function

## Day 5
- Created src/validate.py with 4 checks + validate(df) entry point
- Order: required columns -> dates -> positive rates -> duplicates
- test/test_validate.py: 10 tests, all passing (14 total in repo)
- main.py: validate(df_clean) runs after transform(), before load()
- Deleted src/Extract_Scripts/ (leftover)
- Full run: 7531 rows read, 7531 clean, 0 inserted (idempotent, already loaded)

## Day 6
- Moved load-side code out of main.py into src/load.py
- src/load.py now: make_engine() reads env vars inside; load() does real UPSERT
  (ON CONFLICT ... DO UPDATE) via staging table
- load() returns (inserted, updated) by pre-counting the overlap in staging
- main.py is now a ~40-line orchestrator: extract -> transform -> validate -> load
  and prints a run summary line
- Deleted inline copies of extract/transform/make_engine/ensure_schema/load from main.py
- ensure_schema() removed from main.py; schema remains owned by sql/01_create_schema.sql
- test/test_load.py added (2 unit tests)
- Full suite: 16 passed
- Proof: MAX(loaded_at) after rerun matches the run time -> UPSERT refreshed all 7531
## Day 7 — Repeat-run test (idempotency)

- Ran main.py twice back to back.
- Before:  7531 rows, loaded_at = 2026-09-27 13:18:37 UTC
- Run #1:  0 inserted, 7531 updated (of 7531 attempted)
- Run #2:  0 inserted, 7531 updated (of 7531 attempted)
- After:   7531 rows, loaded_at bumped each run (14:xx / 15:xx UTC)
- Duplicate check:
    SELECT rate_date, currency_code, COUNT(*)
    FROM exchange_rates
    GROUP BY rate_date, currency_code
    HAVING COUNT(*) > 1;
    -> (0 rows)

Conclusion: pipeline is idempotent. The staging-table UPSERT works —
running the same CSV any number of times does not create duplicates.
=====================================
