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

