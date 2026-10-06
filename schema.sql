CREATE TABLE IF NOT EXISTS dim_product (
    product_key  SERIAL PRIMARY KEY,
    code         TEXT UNIQUE NOT NULL,
    product_name TEXT NOT NULL,
    brand        TEXT,
    nutriscore   CHAR(1)
);

CREATE TABLE IF NOT EXISTS dim_category (
    category_key SERIAL PRIMARY KEY,
    category     TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key  INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year      INT,
    month     INT,
    day       INT
);

CREATE TABLE IF NOT EXISTS fact_nutrition (
    product_key   INT REFERENCES dim_product (product_key),
    category_key  INT REFERENCES dim_category (category_key),
    date_key      INT REFERENCES dim_date (date_key),
    energy_kcal   NUMERIC,
    fat           NUMERIC,
    saturated_fat NUMERIC,
    carbohydrates NUMERIC,
    sugars        NUMERIC,
    proteins      NUMERIC,
    salt          NUMERIC,
    PRIMARY KEY (product_key, category_key, date_key)
);