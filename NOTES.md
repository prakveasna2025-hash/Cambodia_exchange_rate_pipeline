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

## Day 8 — Dockerize the ETL

- Created Dockerfile (python:3.11-slim base, WORKDIR /app, pip install,
  COPY code, CMD python main.py)
- Created .dockerignore (venv, .env, .git, data/, docs)
- Created requirements.txt with pinned versions (direct deps only)
- Extended docker-compose.yml with 'etl' service
  - depends_on db with condition: service_healthy
  - POSTGRES_HOST=db  (overrides .env inside the network)
  - ./data/raw mounted read-only into /app/data/raw

Clean-state test:
- docker compose down -v  ->  wiped container, network, pgdata volume
- docker compose up --build  ->  full rebuild + rerun
- Postgres init ran sql/01_create_schema.sql automatically
- etl waited for db healthy, then loaded 7531 rows (7531 ins, 0 upd)
- COUNT(*) = 7531 confirmed after

Run commands:
  docker compose up -d --build
  docker compose exec db psql -U exchange_user -d exchange_db
  docker compose down -v


## Day 9 — Data-quality checks

- Created sql/02_quality_checks.sql with 6 checks (uniqueness, completeness,
  validity, freshness, volume, business_logic)
- Pattern: every check returns exactly one row
  (check_name | status | failed_rows | details)
- All 6 joined with UNION ALL, ordered by check_name
- Adjusted docker-compose.yml so sql/02 isn't auto-run at Postgres init;
  mounted at /sql instead so it can be run manually with psql -f

Interesting finding:
- business_logic originally flagged 16 rows where buying_rate > selling_rate
- Investigated: all present in RAW CSV, tiny reversals (1-91 KHR), spread
  across 2004-2014 — normal pegged-currency noise, not a bug
- Loosened rule to buying_rate > selling_rate + 100 (documented in comment)

Result: 6/6 checks PASS. Screenshot saved.

Run:
  docker compose exec db psql -U exchange_user -d exchange_db -f /sql/02_quality_checks.sql

  ## Day 10 — Analysis queries

- Created sql/03_analysis_queries.sql with 4 queries:
    latest rate (DISTINCT ON), monthly average (DATE_TRUNC + GROUP BY),
    highest/lowest (UNION ALL with parenthesized ORDER BY ... LIMIT),
    day-over-day (window function LAG OVER ORDER BY)
- KHR/USD extremes: ~3950 (Apr 2003) low, ~4286 (Jul 2010) high —
  consistent with the 3000-5000 band from Day 9 quality checks
- Also fixed .dockerignore (was empty → build context 586B after fix)

Run:
  docker compose exec db psql -U exchange_user -d exchange_db \
      -P pager=off -f /sql/03_analysis_queries.sql

      
=====================================
