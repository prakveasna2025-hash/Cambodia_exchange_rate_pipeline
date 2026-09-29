-- Analytical queries on exchange_rates.
-- These are ad-hoc / reporting queries, not checks.
--
-- Run manually:
--   docker compose exec db psql -U exchange_user -d exchange_db -f /sql/03_analysis_queries.sql

-- =====================================================================
-- 1) Latest rate per currency
--    One row per currency: the most recent rate_date and its values.
--    Uses DISTINCT ON (Postgres-specific), which keeps the first row per
--    currency_code according to the ORDER BY.
-- =====================================================================
SELECT DISTINCT ON (currency_code)
       currency_code,
       currency_name,
       rate_date,
       buying_rate,
       selling_rate
FROM exchange_rates
ORDER BY currency_code, rate_date DESC;

-- =====================================================================
-- 2) Monthly average by currency
--    Collapses each month into one row per currency.
--    DATE_TRUNC('month', ...) makes every date in a month the same value,
--    so GROUP BY can collapse them together.
-- =====================================================================
SELECT DATE_TRUNC('month', rate_date)::date AS month,
       currency_code,
       ROUND(AVG(buying_rate),  2) AS avg_buying,
       ROUND(AVG(selling_rate), 2) AS avg_selling,
       COUNT(*) AS days
FROM exchange_rates
GROUP BY DATE_TRUNC('month', rate_date), currency_code
ORDER BY month DESC, currency_code;

-- =====================================================================
-- 3) Highest and lowest in range
--    For each of buying/selling: the extreme value and the day it occurred.
--    "DISTINCT ON (kind)" + ORDER BY lets us pick a different sort order
--    for each row of the union without repeating the whole table scan.
-- =====================================================================
WITH ranked AS (
    (SELECT 'max_buy'  AS kind, rate_date, buying_rate  AS value
     FROM exchange_rates ORDER BY buying_rate  DESC, rate_date LIMIT 1)
    UNION ALL
    (SELECT 'min_buy'  AS kind, rate_date, buying_rate  AS value
     FROM exchange_rates ORDER BY buying_rate  ASC,  rate_date LIMIT 1)
    UNION ALL
    (SELECT 'max_sell' AS kind, rate_date, selling_rate AS value
     FROM exchange_rates ORDER BY selling_rate DESC, rate_date LIMIT 1)
    UNION ALL
    (SELECT 'min_sell' AS kind, rate_date, selling_rate AS value
     FROM exchange_rates ORDER BY selling_rate ASC,  rate_date LIMIT 1)
)
SELECT * FROM ranked ORDER BY kind;
-- =====================================================================
-- 4) Day-over-day change (window function)
--    LAG(col) OVER (ORDER BY rate_date) looks at the previous row.
--    Keeps every row; just adds computed columns.
--    Newest rows first so it's easy to read.
-- =====================================================================
SELECT rate_date,
       buying_rate,
       selling_rate,
       LAG(buying_rate)  OVER (ORDER BY rate_date) AS prev_buying,
       buying_rate  - LAG(buying_rate)  OVER (ORDER BY rate_date) AS dod_buying_change,
       selling_rate - LAG(selling_rate) OVER (ORDER BY rate_date) AS dod_selling_change
FROM exchange_rates
ORDER BY rate_date DESC;

