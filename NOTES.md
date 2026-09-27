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

=====================================
