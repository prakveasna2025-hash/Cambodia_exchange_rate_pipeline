\# Cambodia Exchange Rate Pipeline — Handoff



\## Project goal

Build an ETL pipeline that loads NBC (National Bank of Cambodia) USD/KHR

exchange rate data from a raw CSV into a PostgreSQL data warehouse.

Following a learning plan structured as daily tasks (Day 1, Day 2, ...).



\## Current status: Day 4 complete, Day 5 not started



\## Tech stack

\- Python 3.11 in venv (venv/)

\- pandas for data manipulation

\- SQLAlchemy + psycopg2 for Postgres connection

\- python-dotenv for .env loading

\- pytest for tests

\- PostgreSQL 18 running in Docker (docker-compose.yml)

\- Git + GitHub (prakveasna2025-hash/Cambodia\_exchange\_rate\_pipeline)



\## Project layout

main.py                          entry point — currently orchestrates everything

docker-compose.yml               Postgres 18 in Docker

pytest.ini                       contains: pythonpath = .

.env                             POSTGRES\_USER/PASSWORD/DB/PORT (not in git)

.env.example                     template (in git)

.gitignore                       protects .env, venv, caches, data/processed

NOTES.md                         running notes

HANDOFF.md                       this file

sql/01\_create\_schema.sql         creates exchange\_rates table (runs on first

&#x20;                                container start via /docker-entrypoint-initdb.d)

src/

&#x20; \_\_init\_\_.py                    empty, makes src a package

&#x20; extract.py                     extract\_csv(path) -> DataFrame;

&#x20;                                logs row count + file size

&#x20; transform.py                   transform(df) -> cleaned DataFrame; DROP policy

&#x20; load.py                        EMPTY (Day 5 task)

test/

&#x20; \_\_init\_\_.py

&#x20; test\_extract.py                2 tests

&#x20; test\_transform.py              2 tests

scripts/

&#x20; run\_transform.py               extract -> transform -> write CSV to

&#x20;                                data/processed/exchange\_rates\_clean.csv

&#x20;                                RUN IT WITH: python -m scripts.run\_transform

data/

&#x20; raw/KhmerRiel-USDExchangeRate2003-2023.csv    input, 7531 rows

&#x20; processed/exchange\_rates\_clean.csv            output (gitignored)



\## Data facts

\- Raw CSV columns: date, purchase, sale, midpoint, exchange\_rate, spread\_...

\- We only use: date, purchase, sale

\- 7531 rows, dated 2003-04-01 to 2023-12-31

\- Loaded into Docker Postgres table exchange\_rates with primary key

&#x20; (rate\_date, currency\_code)



\## Target schema (exchange\_rates table)

\- rate\_date        DATE        NOT NULL   (PK)

\- currency\_code    VARCHAR(3)  NOT NULL   (PK)

\- currency\_name    VARCHAR(64) NOT NULL

\- buying\_rate      NUMERIC(18,6)

\- selling\_rate     NUMERIC(18,6)

\- source           VARCHAR(32) NOT NULL

\- loaded\_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()



\## Key design decisions made so far

1\. Extract logs BOTH row count and file size (Day 3 requirement).

2\. Invalid-row policy for transform = DROP with logging.

&#x20;  - Rule 1: unparseable dates -> drop, log count

&#x20;  - Rule 2: duplicate (rate\_date, currency\_code) -> drop, keep last

&#x20;  - errors="coerce" used everywhere so bad values become NaN, not crashes

3\. Load is idempotent (upsert via staging table + ON CONFLICT DO NOTHING).

&#x20;  Rerunning the pipeline inserts 0 duplicates.

4\. Schema is owned by sql/01\_create\_schema.sql (Docker init), NOT by Python.

&#x20;  main.py no longer has ensure\_schema().

5\. Postgres 18 Docker image mounts at /var/lib/postgresql (NOT .../data).

&#x20;  This is a PG-18-specific change.

6\. Data output to data/processed/ uses CSV for easy inspection.

7\. main.py currently contains its OWN inline transform() and load() that

&#x20;  work. The refactor to import from src/transform.py hasn't happened yet.

&#x20;  Day 4's transform module works standalone and is tested, but is not yet

&#x20;  wired into main.py.



\## How to run everything

cd C:\\Users\\ASUS\\OneDrive\\Desktop\\Cambodia\_exchange\_rate\_pipeline

venv\\Scripts\\Activate.ps1

docker compose up -d

docker compose ps                        # wait for "healthy"

python main.py                           # full ETL to Postgres

python -m scripts.run\_transform          # extract -> transform -> CSV

pytest test/ -v                          # run all tests



\## Docker \& database

\- Container name: cambodia\_fx\_db

\- Port: 5432 (host) -> 5432 (container)

\- Credentials in .env: exchange\_user / exchange\_password / exchange\_db

\- psql access:

&#x20;   docker compose exec db psql -U exchange\_user -d exchange\_db

\- To reset the DB completely (loses data, reruns init SQL):

&#x20;   docker compose down -v

&#x20;   docker compose up -d



\## Git state

\- Branch: main

\- Tag day-3-done  -> 474ada4 (Day 3 commit)

\- Tag day-4-done  -> f3c6e60 (Day 4 commit)

\- origin/main still points at 474ada4 — Day 4 not pushed yet

\- Known issue: src/Extract\_Scripts/extract.py is a leftover file from

&#x20; earlier GitHub-web commits. Harmless, but should be deleted.



\## Gotchas learned (IMPORTANT)

\- NEVER edit files on GitHub web UI while local has unpushed commits.

&#x20; This caused a rebase conflict mess.

\- To roll back: git reset --hard <tag> then git push --force

\- To verify remote state for real: git ls-remote origin main

\- pytest needs pythonpath = . in pytest.ini for src/ imports to resolve

\- Scripts in subfolders: run with `python -m scripts.<name>`, NOT

&#x20; `python scripts\\<name>.py` (import path issue)

\- In Python REPL, editing a file does NOT reload it. Exit and re-enter

&#x20; the REPL, or use importlib.reload.

\- Python REPL prompt is `>>>` — PowerShell prompt is `PS C:\\...>`.

&#x20; Python code only works at `>>>`.

\- pandas auto-detects numeric types when reading CSV, but explicit

&#x20; pd.to\_numeric(..., errors="coerce") is safer for future data.

\- On Windows, pandas datetime dtype shows as datetime64\[us],

&#x20; not datetime64\[ns]. Both are fine.

\- Notepad's Ctrl+A + paste is not always reliable for full overwrite.

- Notepad's Ctrl+A + paste is not always reliable for full overwrite.
  Always verify with Get-Content <file> | Select-Object -First 5 after saving.

- If origin/main has commits you don't have (e.g. README edited on GitHub web UI):
    1. git fetch origin
    2. git --no-pager log --oneline --graph --all -10   (see what's there)
    3. git pull --rebase origin main
    4. If a tag pointed at the old commit: git tag -f <tag> <new-sha>
    5. git push origin main
    6. git push origin <tag> --force
- git log opens a pager; press `q` to exit (or use `git --no-pager log ...`)

&#x20; Always verify with Get-Content <file> | Select-Object -First 5 after saving.



\## Day 5 task (next)

Move load() and make\_engine() from main.py into src/load.py.

\- Same 3-step pattern as Day 3 (extract) and Day 4 (transform):

&#x20; 1. Write src/load.py piece by piece, running after each

&#x20; 2. Add tests in test/test\_load.py

&#x20; 3. Wire into main.py (remove inline versions)

\- Then main.py becomes a tiny orchestrator (\~20 lines).



\## Teaching style that worked best

\- Go SLOW. One small piece at a time.

\- After each piece: run it, look at output, understand, then next.

\- No walls of code. No "paste this 60-line file."

\- Use the REPL heavily so the user can SEE the data (like SQL SELECT).

\- Explain the WHY before the code.

\- Tie new concepts back to the user's existing SQL / Data Warehouse knowledge.

\- If user says "lost" or "overwhelmed", back up and slow down immediately.



\## User background

\- Experienced with SQL and Data Warehouse design

\- Newer to Python and pandas

\- Learns by seeing outputs (SELECT-style) and understanding why

\- Prefers incremental building with verification at each step

## Day 5
\- Created src/validate.py with 4 checks + validate(df) entry point
\- Order: required columns -> dates -> positive rates -> duplicates
\- test/test_validate.py: 10 tests, all passing (14 total in repo)
\- main.py: validate(df_clean) runs after transform(), before load()
\- Deleted src/Extract_Scripts/ (leftover)
\- Full run: 7531 rows read, 7531 clean, 0 inserted (idempotent, already loaded)

## Day 6 (complete)
- src/load.py: make_engine() + load() (UPSERT via staging, returns inserted/updated)
- main.py: tiny orchestrator with run summary (extracted/valid/rejected/inserted/updated)
- test/test_load.py added
- 16 tests passing

## Day 7 task (next)
TBD by user. Options:
- Integration test for load() against a throwaway schema
- GitHub Actions CI (run pytest on push)
- Add CLI flags (--csv path, --dry-run)
- Handle rejected rows in a dead-letter output (data/processed/rejected.csv)

## Current status: Day 7 complete

## Day 7 (complete) — Repeat-run test
- Ran main.py twice back to back
- Before:  7531 rows, loaded_at = 2026-09-27 13:18:37 UTC
- Run #1:  0 inserted, 7531 updated
- Run #2:  0 inserted, 7531 updated
- After:   7531 rows, loaded_at bumped each run
- Duplicate check: SELECT ... GROUP BY rate_date, currency_code HAVING COUNT(*) > 1 -> (0 rows)
- Conclusion: pipeline is idempotent


## Day 8 (complete) — Dockerize the ETL

New files:
- Dockerfile       python:3.11-slim, WORKDIR /app, pip install from requirements.txt,
                   COPY main.py + src/, CMD ["python","main.py"]
- .dockerignore    excludes venv/, .env, .git/, data/, __pycache__/, docs
- requirements.txt pinned: pandas==3.0.6, SQLAlchemy==2.1.0,
                   psycopg2-binary==2.9.13, python-dotenv==1.2.3

Changed:
- docker-compose.yml: added 'etl' service
    build: .
    depends_on: db (condition: service_healthy)
    env_file: .env
    environment: POSTGRES_HOST=db          <- key: container-to-container hostname
    volumes: ./data/raw -> /app/data/raw:ro

Clean-state test passed:
- docker compose down -v  (wipes pgdata volume)
- docker compose up --build
- Postgres initialized, schema ran, etl waited for health, loaded 7531 rows
  (7531 inserted, 0 updated — first-ever load)
- SELECT COUNT(*) = 7531

How to run:
- docker compose up -d --build       # start stack, run etl once
- docker compose exec db psql -U exchange_user -d exchange_db
- docker compose down -v             # full reset (loses data)

## Day 9 (complete) — Data-quality checks

New file: sql/02_quality_checks.sql
- Six checks, each returning one row (check_name | status | failed_rows | details)
- uniqueness    : no duplicate (rate_date, currency_code) pairs
- completeness  : no NULLs in required columns
- validity      : positive rates, plausible dates, known currency codes
- freshness     : last loaded_at within 24h
- volume        : row count 7000-8000
- business_logic: buying_rate < selling_rate + 100, rates within 3000-5000

Finding during Day 9:
- Original business-logic rule (buying_rate > selling_rate) FAILED with 16 rows
- Investigation: all 16 had buying > selling by 1-91 KHR, spread across
  2004-2014, present in the RAW CSV (not a transform bug)
- Diagnosis: normal pegged-currency noise for KHR on quiet days
- Fix: loosened rule to buying_rate > selling_rate + 100 (tolerance)
- Result: all 6 checks PASS

How to run:
  docker compose exec db psql -U exchange_user -d exchange_db -f /sql/02_quality_checks.sql

  - docker-compose.yml: db service now mounts only 01_create_schema.sql at
  /docker-entrypoint-initdb.d/, and the whole ./sql folder at /sql (read-only)
  so quality checks can be run manually without Postgres auto-running them
  at init time.

  - Postgres auto-runs EVERY .sql file in /docker-entrypoint-initdb.d at first
  init. To keep extra SQL files out of init, mount them somewhere else
  (e.g. /sql) and run them with psql -f.
- A data-quality check that always PASSes teaches nothing. If a check ever
  fails on real data, investigate before "fixing" the check:
    1. Is it the source (bad raw data) or the pipeline (transform bug)?
    2. Is it a real anomaly or expected behavior for this domain?
    3. Only then decide: fix the data, fix the pipeline, or loosen the rule.
- UNION ALL (not UNION) when stacking summary rows that are guaranteed unique.

## Day 10 task (next)
## Day 10 (complete) — Analysis queries

New file: sql/03_analysis_queries.sql
- Four queries:
    1. Latest rate per currency       (DISTINCT ON)
    2. Monthly average by currency    (DATE_TRUNC + GROUP BY)
    3. Highest/lowest in range        (UNION ALL with parenthesized branches)
    4. Day-over-day change            (window function: LAG OVER ORDER BY)

Findings:
- KHR/USD has ranged roughly 3950-4286 over 2003-2023
  (min 2003-04-01, max 2010-07-01 for buying, 2005-07-29 for selling)
- These extremes align with the 3000-5000 band used in Day 9's quality check
- December 2023 avg: buying 4100.94 / selling 4110.74, 31 days

Gotcha found:
- In a UNION ALL, each branch with its own ORDER BY ... LIMIT must be
  wrapped in parentheses. Otherwise Postgres binds the ORDER BY to the
  whole union and errors with "syntax error at or near UNION".

Also fixed on this day:
- .dockerignore was empty (0 bytes). Populated it so the build context
  drops from tens of MB to 586 bytes.

How to run:
  docker compose exec db psql -U exchange_user -d exchange_db \
      -P pager=off -f /sql/03_analysis_queries.sql

Note: query 4 returns 7531 rows; use -P pager=off and expect scrolling.

## Day 11 task (next)
## Day 11 (complete) — README + architecture diagram
- Rewrote README.md using a 10-section outline (title, overview,
  architecture, tech stack, structure, data source, how to run, quality
  checks, testing, future work)
- Created docs/diagrams/pipeline.drawio (source, editable in draw.io)
- PENDING: export pipeline.svg to docs/diagrams/ — README image reference
  is currently a broken link until this is added