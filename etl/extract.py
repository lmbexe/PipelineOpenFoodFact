import json
import os
import time
from datetime import date
from pathlib import Path

import requests

HEADERS = {"User-Agent": "MonProjetDataEng/0.1 (ton-email@exemple.fr)"}
URL = "https://world.openfoodfacts.org/api/v2/search"
FIELDS = "code,product_name,brands,nutriscore_grade,last_modified_t,nutriments"
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
RAW_DIR = DATA_DIR / "raw"


def get_with_retry(url, params, max_retries=4):
    for attempt in range(1, max_retries + 1):
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if r.status_code in (429, 500, 502, 503, 504):
            wait = 5 * attempt
            print(f"Erreur {r.status_code}, nouvelle tentative dans {wait}s")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError("API indisponible")


def extract(category, pages=5, page_size=100):
    products = []
    for page in range(1, pages + 1):
        params = {
            "categories_tags_en": category,
            "page_size": page_size,
            "page": page,
            "fields": FIELDS,
        }
        batch = get_with_retry(URL, params).json().get("products", [])
        for p in batch:
            p["category"] = category
        products.extend(batch)
        print(f"{category} page {page}: {len(batch)} produits")
        time.sleep(7)  # la recherche est limitée à 10 requêtes par minute

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{category}_{date.today()}.json"
    raw_path.write_text(json.dumps(products, ensure_ascii=False), encoding="utf-8")
    return raw_path