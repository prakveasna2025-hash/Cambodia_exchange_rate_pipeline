# Cambodia Daily Exchange-Rate Pipeline

A reproducible ETL pipeline that loads Cambodia's official USD/KHR exchange-rate
history into PostgreSQL, validates it, and makes it queryable for trend analysis.

## 🎯 Business purpose

Analysts need reliable access to daily official currency exchange-rate data in a
clean database table — not a raw CSV — to answer questions like: what was the
USD/KHR monthly average, and how has it changed over time? This project builds
that pipeline end to end.

## 🏗️ Architecture

```
data/raw CSV → extract.py → transform.py → clean records → load.py → PostgreSQL
                                                                  ↓
                                                   quality_checks.sql → results
```

- **Raw data**: immutable downloaded CSV, never edited by hand
- **Python ETL**: extracts, cleans, validates, and loads the data
- **PostgreSQL**: stores the structured historical rates
- **Docker Compose**: runs Postgres and the ETL consistently
- **SQL checks**: test freshness, nulls, duplicates, and valid ranges

## 🧰 Tech stack

Python · Pandas · PostgreSQL · Docker Compose

## 📊 Data source

Historical Khmer Riel–USD exchange rate data (2003–2023), sourced from
Cambodia's Data EF portal (data.mef.gov.kh), originally published by the
National Bank of Cambodia.

| Field | Meaning |
|---|---|
| `rate_date` | Date the rate applies to |
| `currency_code` | Currency priced against KHR (e.g. USD) |
| `buying_rate_khr` | Bank buying rate in KHR |
| `selling_rate_khr` | Bank selling rate in KHR |
| `midpoint_rate_khr` | Midpoint rate in KHR |
| `source_name` | Provenance (e.g. NBC / Data EF) |
| `source_url` | Where the record originated |
| `loaded_at` | Timestamp written by the pipeline |

Primary key: `rate_date` + `currency_code` (prevents duplicate daily loads).

## ✅ Prerequisites

- Python 3.11+
- Docker Desktop
- Git

## ⚙️ Setup

```bash
git clone <your-repo-url>
cd cambodia-exchange-rate-pipeline
python -m venv venv
venv\Scripts\Activate.ps1      # Windows
pip install -r requirements.txt
cp .env.example .env           # fill in your own local values
```

## ▶️ How to run

```bash
docker compose up --build
```

This starts PostgreSQL and runs the ETL pipeline (extract → transform →
validate → load) against it. Rerunning is safe — the pipeline uses UPSERT, so
it will not create duplicate rows.

## 🗄️ Data model and quality checks

The `exchange_rates` table enforces `NOT NULL` on required fields and unique
`(rate_date, currency_code)` pairs. `sql/02_quality_checks.sql` verifies
uniqueness, completeness, validity, freshness, volume, and basic business
logic after every load.

## 📈 Example analysis

See `sql/03_analysis_queries.sql` for: latest available rate, monthly
average by currency, highest/lowest rate in a date range, and day-over-day
change.

## 🚀 Limitations & Version 2 roadmap

This version loads a static historical CSV (through Dec 2023), not live data.
Version 2 plans:
- Replace the CSV with the official daily API
- Add scheduled runs
- Add a cloud destination
- Optional dashboard

## 📍 Status

🚧 In progress — see the project roadmap for current build stage.
