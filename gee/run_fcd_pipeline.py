"""
Parameterized FCD pipeline runner.
Exports FCD GeoTIFFs to Google Drive, then uploads them
to GitHub Releases as release assets (no GCS required).
"""
import argparse
import json
import os
import time
from datetime import datetime, timezone
import ee
from auth import initialize_ee
from fcd_algorithm import build_fcd

DATE_WINDOWS = {
    "2020": {"start": "2020-02-01", "end": "2020-03-31"},
    "2021": {"start": "2021-02-01", "end": "2021-03-31"},
    "2022": {"start": "2022-02-01", "end": "2022-03-31"},
    "2023": {"start": "2023-02-01", "end": "2023-03-31"},
    "2024": {"start": "2024-02-01", "end": "2024-03-31"},
    "2025": {"start": "2025-02-01", "end": "2025-03-31"},
}

EXPORT_FOLDER = "FCD_exports"


def export_fcd_to_drive(fcd_img, geom, label):
    """Export FCD GeoTIFF to Google Drive folder."""
    task = ee.batch.Export.image.toDrive(
        image=fcd_img,
        description=f"FCD_{label}",
        folder=EXPORT_FOLDER,
        fileNamePrefix=f"FCD_{label}",
        region=geom,
        scale=10,
        crs="EPSG:4326",
        maxPixels=1e13,
        fileFormat="GeoTIFF",
    )
    task.start()
    print(f"\U0001f680 Drive export started : FCD_{label}.tif → Drive/{EXPORT_FOLDER}/")
    return task


def wait_for_tasks(tasks, poll_interval=30, max_minutes=180):
    """Block until all tasks complete or timeout."""
    pending  = {t.id: t for t in tasks}
    deadline = time.time() + max_minutes * 60

    while pending and time.time() < deadline:
        for task_id in list(pending):
            status = ee.data.getTaskStatus(task_id)[0]
            state  = status["state"]
            name   = status.get("description", task_id)
            if state == "COMPLETED":
                print(f"✅ COMPLETED : {name}")
                del pending[task_id]
            elif state in ("FAILED", "CANCELLED"):
                print(f"❌ {state} : {name} — {status.get('error_message', '')}")
                del pending[task_id]
            else:
                print(f"⏳ {state} : {name}")
        if pending:
            time.sleep(poll_interval)

    return len(pending) == 0


def run_pipeline(aoi_name, aoi_asset, years, cloud_pct):
    initialize_ee()
    aoi_geom = ee.FeatureCollection(aoi_asset).geometry()
    tasks    = []
    results  = {}

    for year_label, cfg in years.items():
        print(f"\n{'='*52}")
        print(f"Processing : {aoi_name} — {year_label}")
        print(f"Date range : {cfg['start']} → {cfg['end']}")

        fcd         = build_fcd(aoi_geom, cfg["start"], cfg["end"],
                                f"{aoi_name}_{year_label}", cloud_pct)
        scene_count = fcd.get("scene_count").getInfo()
        print(f"Scenes     : {scene_count}")

        task = export_fcd_to_drive(fcd, aoi_geom, f"{aoi_name}_{year_label}")
        tasks.append(task)
        results[year_label] = {
            "task_id":     task.id,
            "label":       f"{aoi_name}_{year_label}",
            "scene_count": scene_count,
            "filename":    f"FCD_{aoi_name}_{year_label}.tif",
        }

    # Wait for all exports to finish before the workflow uploads to GitHub
    print("\n⏳ Waiting for all GEE Drive exports to complete...")
    all_done = wait_for_tasks(tasks)

    manifest = {
        "aoi":      aoi_name,
        "run_time": datetime.now(timezone.utc).isoformat(),
        "all_done": all_done,
        "tasks":    results,
    }
    with open("gee_task_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("\n📄 Manifest written : gee_task_manifest.json")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--aoi-name",  required=True)
    parser.add_argument("--aoi-asset", required=True)
    parser.add_argument("--years",     default="2025")
    parser.add_argument("--cloud-pct", type=float, default=1.0)
    args = parser.parse_args()

    selected = {y: DATE_WINDOWS[y] for y in args.years.split(",") if y in DATE_WINDOWS}
    if not selected:
        raise ValueError(f"No valid years. Available: {list(DATE_WINDOWS.keys())}")

    run_pipeline(args.aoi_name, args.aoi_asset, selected, args.cloud_pct)
