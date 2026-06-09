"""
Reads GitHub Release assets for a given tag and inserts
their COG URLs into the fcd_rasters table in PostGIS.
Usage: python ingest_release_urls.py <tag>  (e.g. fcd-2025)
"""
import os, sys, requests
from sqlalchemy import create_engine, text

GITHUB_REPO  = os.environ["GITHUB_REPO"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
DATABASE_URL = os.environ["DATABASE_URL"].replace("+asyncpg", "")

engine = create_engine(DATABASE_URL)


def get_release_assets(tag: str) -> list:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{tag}"
    r   = requests.get(
        url,
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}",
                 "Accept": "application/vnd.github+json"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json().get("assets", [])


def parse_label(name: str):
    """FCD_TamilNadu_2025.tif  ->  ('TamilNadu', '2025')"""
    stem  = name.replace(".tif", "").replace(".TIF", "")
    parts = stem.split("_")
    if len(parts) >= 3:
        return "_".join(parts[1:-1]), parts[-1]
    return stem, "unknown"


def ingest(tag: str) -> None:
    assets     = get_release_assets(tag)
    tif_assets = [a for a in assets if a["name"].lower().endswith(".tif")]
    print(f"Found {len(tif_assets)} .tif asset(s) in release '{tag}'")

    with engine.connect() as conn:
        for asset in tif_assets:
            aoi_name, year = parse_label(asset["name"])
            url = asset["browser_download_url"]

            run = conn.execute(
                text(
                    "SELECT id FROM fcd_runs "
                    "WHERE year=:y ORDER BY created_at DESC LIMIT 1"
                ),
                {"y": int(year) if year.isdigit() else 0},
            ).fetchone()
            run_id = str(run[0]) if run else None

            aoi = conn.execute(
                text(
                    "SELECT id FROM admin_units "
                    "WHERE name ILIKE :n LIMIT 1"
                ),
                {"n": f"%{aoi_name}%"},
            ).fetchone()
            aoi_id = str(aoi[0]) if aoi else None

            conn.execute(
                text(
                    """INSERT INTO fcd_rasters (run_id, aoi_id, year, raster_type, cog_url)
                       VALUES (:run_id, :aoi_id, :year, 'fcd', :url)
                       ON CONFLICT DO NOTHING"""
                ),
                {"run_id": run_id, "aoi_id": aoi_id,
                 "year": int(year) if year.isdigit() else 0,
                 "url": url},
            )
            print(f"  \u2705 Ingested: {asset['name']}")
        conn.commit()
    print("Ingest complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_release_urls.py <tag>")
        sys.exit(1)
    ingest(sys.argv[1])
