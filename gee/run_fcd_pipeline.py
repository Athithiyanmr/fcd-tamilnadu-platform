"""
Called by GitHub Actions fcd_annual_run.yml.
Authenticates with GEE via service account, exports FCD COGs to Google Drive,
waits for task completion, and writes gee_task_manifest.json.
"""
import os, json, time, argparse, tempfile
import ee

SA_KEY_JSON = os.environ["GEE_SERVICE_ACCOUNT_KEY"]
SA_EMAIL    = os.environ["GEE_SERVICE_ACCOUNT_EMAIL"]
GEE_PROJECT = os.environ["GEE_PROJECT_ID"]

DRIVE_FOLDER = "fcd_tamilnadu_exports"
POLL_SEC     = 60
MAX_WAIT_SEC = 3 * 3600


def authenticate() -> None:
    import json as _json
    key = _json.loads(SA_KEY_JSON)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        _json.dump(key, f)
        keyfile = f.name
    credentials = ee.ServiceAccountCredentials(SA_EMAIL, keyfile)
    ee.Initialize(credentials, project=GEE_PROJECT)
    print("\u2705 GEE authenticated")


def build_fcd_image(aoi: ee.Geometry, start: str, end: str, cloud_pct: float) -> ee.Image:
    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_pct))
        .select(["B3", "B4", "B8"])
        .median()
        .divide(10000)
        .clip(aoi)
    )

    green = s2.select("B3")
    red   = s2.select("B4")
    nir   = s2.select("B8")

    eps       = 1e-10
    ndvi      = nir.subtract(red).divide(nir.add(red).add(eps))
    ndwi      = green.subtract(nir).divide(green.add(nir).add(eps))
    bi        = nir.add(green).add(red).divide(nir.add(green).subtract(red).add(eps))
    si        = ee.Image(1).subtract(green).multiply(ee.Image(1).subtract(red)).sqrt()

    bare       = ndvi.lt(0.25).And(bi.gt(2)).And(si.lt(0.92)).multiply(5)
    grass      = ndvi.gt(0.25).multiply(4)
    low_forest = (
        ndvi.gt(0.25).And(ndvi.lte(0.45))
        .And(bi.lt(2)).And(si.gte(0.92)).And(si.lte(0.95))
        .multiply(3)
    )
    hi_forest  = ndvi.gt(0.45).And(bi.lt(2)).And(si.gt(0.95)).multiply(2)
    water      = ndwi.gt(0.2).multiply(1)

    fcd = (
        ee.Image(0)
        .where(bare.gt(0),       bare)
        .where(grass.gt(0),      grass)
        .where(low_forest.gt(0), low_forest)
        .where(hi_forest.gt(0),  hi_forest)
        .where(water.gt(0),      water)
        .rename("FCD")
        .toUint8()
    )
    return fcd


def export_to_drive(
    image: ee.Image,
    aoi: ee.Geometry,
    description: str,
) -> ee.batch.Task:
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description,
        folder=DRIVE_FOLDER,
        fileNamePrefix=description,
        region=aoi,
        scale=10,
        crs="EPSG:4326",
        maxPixels=1e13,
        fileFormat="GeoTIFF",
    )
    task.start()
    print(f"  \U0001f680 Task started: {description} (id={task.id})")
    return task


def wait_for_tasks(tasks_meta: list) -> list:
    print(f"\n\u23f3 Waiting for {len(tasks_meta)} GEE task(s)...")
    pending  = {t["id"]: t for t in tasks_meta}
    results  = []
    elapsed  = 0

    while pending and elapsed < MAX_WAIT_SEC:
        time.sleep(POLL_SEC)
        elapsed += POLL_SEC
        done_keys = []
        all_tasks = ee.batch.Task.list()
        for task_obj in all_tasks:
            if task_obj.id not in pending:
                continue
            state = task_obj.state
            meta  = pending[task_obj.id]
            if state == "COMPLETED":
                print(f"  \u2705 {meta['description']} \u2014 COMPLETED")
                meta["state"] = "COMPLETED"
                results.append(meta)
                done_keys.append(task_obj.id)
            elif state in ("FAILED", "CANCELLED"):
                print(f"  \u274c {meta['description']} \u2014 {state}")
                meta["state"] = state
                results.append(meta)
                done_keys.append(task_obj.id)
        for k in done_keys:
            del pending[k]

    for meta in pending.values():
        print(f"  \u26a0\ufe0f  Timeout: {meta['description']}")
        meta["state"] = "TIMEOUT"
        results.append(meta)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run FCD pipeline via GEE")
    parser.add_argument("--aoi-name",  required=True)
    parser.add_argument("--aoi-asset", required=True)
    parser.add_argument("--years",     required=True)
    parser.add_argument("--cloud-pct", type=float, default=1.0)
    args = parser.parse_args()

    authenticate()

    aoi   = ee.FeatureCollection(args.aoi_asset).geometry()
    years = [y.strip() for y in args.years.split(",")]

    tasks_meta = []
    for year in years:
        print(f"\n\U0001f4c5 Processing year {year}...")
        image = build_fcd_image(
            aoi,
            start=f"{year}-01-01",
            end=f"{year}-12-31",
            cloud_pct=args.cloud_pct,
        )
        desc = f"FCD_{args.aoi_name}_{year}"
        task = export_to_drive(image, aoi, desc)
        tasks_meta.append({
            "id":          task.id,
            "description": desc,
            "year":        year,
            "aoi_name":    args.aoi_name,
            "state":       "RUNNING",
        })

    results = wait_for_tasks(tasks_meta)

    manifest = {"aoi_name": args.aoi_name, "tasks": results}
    with open("gee_task_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("\n\U0001f4c4 gee_task_manifest.json written")

    failed = [t for t in results if t["state"] != "COMPLETED"]
    if failed:
        print(f"\n\u274c {len(failed)} task(s) did not complete:")
        for t in failed:
            print(f"   {t['description']}: {t['state']}")
        raise SystemExit(1)

    print("\n\U0001f389 All GEE tasks completed successfully.")


if __name__ == "__main__":
    main()
