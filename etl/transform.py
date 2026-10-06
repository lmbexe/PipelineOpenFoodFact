import json

import pandas as pd

NUTRIENTS = [
    "energy-kcal_100g", "fat_100g", "saturated-fat_100g",
    "carbohydrates_100g", "sugars_100g", "proteins_100g", "salt_100g",
]


def transform(raw_path):
    products = json.loads(raw_path.read_text(encoding="utf-8"))

    rows = []
    for p in products:
        nutriments = p.get("nutriments", {})
        row = {
            "code": p.get("code"),
            "product_name": p.get("product_name"),
            "brand": p.get("brands"),
            "nutriscore": p.get("nutriscore_grade"),
            "last_modified_t": p.get("last_modified_t"),
            "category": p.get("category"),
        }
        for n in NUTRIENTS:
            row[n] = nutriments.get(n)
        rows.append(row)
    df = pd.DataFrame(rows)

    df = df.dropna(subset=["code", "product_name"])
    df["product_name"] = df["product_name"].str.strip()
    df = df[df["product_name"] != ""]
    df["brand"] = df["brand"].fillna("").str.split(",").str[0].str.strip().str.lower()
    df["brand"] = df["brand"].replace("", pd.NA)
    df["nutriscore"] = df["nutriscore"].where(df["nutriscore"].isin(list("abcde")))
    df["last_modified"] = pd.to_datetime(df["last_modified_t"], unit="s")
    df = df.drop(columns="last_modified_t")
    df = df.drop_duplicates(subset="code")
    return df