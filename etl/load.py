import os
from datetime import date
from pathlib import Path

import psycopg2

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
CLEAN_DIR = DATA_DIR / "clean"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


def load(df):
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CLEAN_DIR / "products.csv"
    df.to_csv(out_path, index=False)
    return out_path


def conn_params():
    return dict(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "warehouse"),
        user=os.getenv("DB_USER", "de"),
        password=os.getenv("DB_PASSWORD", "de_password"),
    )


def load_to_db(df):
    df = df.astype(object).where(df.notna(), None)
    today = date.today()
    date_key = int(today.strftime("%Y%m%d"))

    conn = psycopg2.connect(**conn_params())
    try:
        with conn, conn.cursor() as cur:
            cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))

            cur.execute(
                """INSERT INTO dim_date (date_key, full_date, year, month, day)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (date_key, today, today.year, today.month, today.day),
            )

            for r in df.to_dict("records"):
                cur.execute(
                    """INSERT INTO dim_product (code, product_name, brand, nutriscore)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (code) DO UPDATE SET
                           product_name = EXCLUDED.product_name,
                           brand = EXCLUDED.brand,
                           nutriscore = EXCLUDED.nutriscore
                       RETURNING product_key""",
                    (r["code"], r["product_name"], r["brand"], r["nutriscore"]),
                )
                product_key = cur.fetchone()[0]

                cur.execute(
                    """INSERT INTO dim_category (category) VALUES (%s)
                       ON CONFLICT (category) DO UPDATE SET category = EXCLUDED.category
                       RETURNING category_key""",
                    (r["category"],),
                )
                category_key = cur.fetchone()[0]

                cur.execute(
                    """INSERT INTO fact_nutrition
                           (product_key, category_key, date_key, energy_kcal, fat,
                            saturated_fat, carbohydrates, sugars, proteins, salt)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       ON CONFLICT (product_key, category_key, date_key) DO UPDATE SET
                           energy_kcal = EXCLUDED.energy_kcal, fat = EXCLUDED.fat,
                           saturated_fat = EXCLUDED.saturated_fat,
                           carbohydrates = EXCLUDED.carbohydrates,
                           sugars = EXCLUDED.sugars, proteins = EXCLUDED.proteins,
                           salt = EXCLUDED.salt""",
                    (product_key, category_key, date_key,
                     r["energy-kcal_100g"], r["fat_100g"], r["saturated-fat_100g"],
                     r["carbohydrates_100g"], r["sugars_100g"], r["proteins_100g"],
                     r["salt_100g"]),
                )
    finally:
        conn.close()

    return len(df)