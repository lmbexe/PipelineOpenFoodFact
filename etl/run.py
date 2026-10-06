import pandas as pd

from etl.extract import extract
from etl.load import load, load_to_db
from etl.transform import transform

CATEGORIES = ["breakfast-cereals", "chocolates"]


def run_pipeline(categories=None):
    categories = categories or CATEGORIES
    frames = [transform(extract(c)) for c in categories]
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(subset=["code", "category"])
    csv_path = load(df)
    n = load_to_db(df)
    print(f"{len(df)} produits propres écrits dans {csv_path}, {n} lignes chargées en base")
    return df