-- Data-quality checks for exchange_rates.
-- Each check returns exactly one row: check_name | status | failed_rows | details.
-- Every check should show status = 'PASS' on healthy data.
--
-- Run manually:
--   docker compose exec db psql -U exchange_user -d exchange_db -f /sql/02_quality_checks.sql

-- 1) Uniqueness: no duplicate (rate_date, currency_code) pairs.
SELECT 'uniqueness' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS failed_rows,
       'duplicate (rate_date, currency_code) pairs' AS details
FROM (
    SELECT rate_date, currency_code
    FROM exchange_rates
    GROUP BY rate_date, currency_code
    HAVING COUNT(*) > 1
) d

UNION ALL

-- 2) Completeness: no NULLs in required columns.
SELECT 'completeness',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       COUNT(*),
       'NULLs in required columns'
FROM exchange_rates
WHERE rate_date      IS NULL
   OR currency_code  IS NULL
   OR currency_name  IS NULL
   OR buying_rate    IS NULL
   OR selling_rate   IS NULL
   OR source         IS NULL

UNION ALL

-- 3) Validity: positive rates, plausible dates, known currency codes.
SELECT 'validity',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       COUNT(*),
       'non-positive rates, out-of-range dates, or unknown currency codes'
FROM exchange_rates
WHERE buying_rate   <= 0
   OR selling_rate  <= 0
   OR rate_date      < DATE '2000-01-01'
   OR rate_date      > CURRENT_DATE
   OR currency_code NOT IN ('USD')

UNION ALL

-- 4) Freshness: loaded within the last 24 hours.
SELECT 'freshness',
       CASE WHEN MAX(loaded_at) >= NOW() - INTERVAL '24 hours' THEN 'PASS' ELSE 'FAIL' END,
       CASE WHEN MAX(loaded_at) >= NOW() - INTERVAL '24 hours' THEN 0 ELSE 1 END,
       CONCAT('last load: ', COALESCE(MAX(loaded_at)::text, 'never'))
FROM exchange_rates

UNION ALL

-- 5) Volume: row count within expected range (7000-8000).
SELECT 'volume',
       CASE WHEN COUNT(*) BETWEEN 7000 AND 8000 THEN 'PASS' ELSE 'FAIL' END,
       CASE WHEN COUNT(*) BETWEEN 7000 AND 8000 THEN 0 ELSE 1 END,
       CONCAT('row count: ', COUNT(*))
FROM exchange_rates

UNION ALL

-- 6) Business logic: buy < sell (with 100 KHR tolerance for pegged-currency noise),
--    and both rates within historical USD/KHR band.
SELECT 'business_logic',
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       COUNT(*),
       'buying > selling by >100 KHR, or rate outside 3000-5000'
FROM exchange_rates
WHERE buying_rate > selling_rate + 100
   OR buying_rate NOT BETWEEN 3000 AND 5000
   OR selling_rate NOT BETWEEN 3000 AND 5000

ORDER BY check_name;