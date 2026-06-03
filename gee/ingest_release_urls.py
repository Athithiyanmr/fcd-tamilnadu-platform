"""
After GitHub Release is created, record the public download URLs
for each GeoTIFF asset into PostGIS fcd_rasters table.
"""
import os
import re
import sys
import requests
from sqlalchemy import create_engine, text

GITHUB_REPO  = os.environ.get("GITHUB_REPO", "Athithiyanmr/fcd-tamilnadu-platform")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
DATABASE_URL = os.environ["DATABASE_URL"]


def get_release_assets(tag):
    url     = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{tag}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    res     = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json().get("assets", [])


def ingest(tag):
    engine = create_engine(DATABASE_URL)
    assets = get_release_assets(tag)
    tifs   = [a for a in assets if a["name"].endswith(".tif")]

    if not tifs:
        print(f"⚠️  No .tif assets found in release {tag}")
        return

    with engine.connect() as conn:
        for asset in tifs:
            name    = asset["name"]                    # e.g. FCD_TamilNadu_2025.tif
            url     = asset["browser_download_url"]    # public HTTPS URL
            m       = re.search(r"_(\d{4})\.tif$", name)
            year    = int(m.group(1)) if m else 0

            conn.execute(text("""
                INSERT INTO fcd_rasters (id, year, raster_type, cog_url, created_at)
                VALUES (gen_random_uuid(), :year, 'fcd', :cog_url, now())
                ON CONFLICT DO NOTHING;
            """), {"year": year, "cog_url": url})
            print(f"📥 Ingested : {name} → {url}")
        conn.commit()


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "fcd-2025"
    ingest(tag)
