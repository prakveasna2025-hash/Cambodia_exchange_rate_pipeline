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

