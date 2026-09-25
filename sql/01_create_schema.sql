
CREATE TABLE IF NOT EXISTS exchange_rates (
    rate_date      DATE        NOT NULL,
    currency_code  VARCHAR(3)  NOT NULL,
    currency_name  VARCHAR(64) NOT NULL,
    buying_rate    NUMERIC(18, 6),
    selling_rate   NUMERIC(18, 6),
    source         VARCHAR(32) NOT NULL,
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT exchange_rates_pkey PRIMARY KEY (rate_date, currency_code)
);
