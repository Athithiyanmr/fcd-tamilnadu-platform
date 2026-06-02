"""Parameterized FCD pipeline runner — starts GEE export tasks and writes a manifest."""
import argparse
import json
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


def export_fcd_to_gcs(fcd_img, geom, label, bucket, folder="FCD_exports"):
    task = ee.batch.Export.image.toCloudStorage(
        image=fcd_img,
        description=f"FCD_{label}",
        bucket=bucket,
        fileNamePrefix=f"{folder}/FCD_{label}",
        region=geom,
        scale=10,
        crs="EPSG:4326",
        maxPixels=1e13,
        fileFormat="GeoTIFF",
        formatOptions={"cloudOptimized": True},
    )
    task.start()
    print(f"🚀 Task started: FCD_{label} → gs://{bucket}/{folder}/FCD_{label}.tif")
    return task


def run_pipeline(aoi_name, aoi_asset, years, cloud_pct, bucket):
    initialize_ee()
    aoi_geom = ee.FeatureCollection(aoi_asset).geometry()
    results  = {}

    for year_label, cfg in years.items():
        print(f"\n{'='*52}")
        print(f"Processing : {aoi_name} — {year_label}")
        print(f"Date range : {cfg['start']} → {cfg['end']}")

        fcd         = build_fcd(aoi_geom, cfg["start"], cfg["end"],
                                f"{aoi_name}_{year_label}", cloud_pct)
        scene_count = fcd.get("scene_count").getInfo()
        print(f"Scenes     : {scene_count}")

        task = export_fcd_to_gcs(fcd, aoi_geom, f"{aoi_name}_{year_label}", bucket)
        results[year_label] = {
            "task_id":     task.id,
            "status":      "started",
            "scene_count": scene_count,
            "label":       f"{aoi_name}_{year_label}",
        }

    manifest = {
        "aoi":      aoi_name,
        "run_time": datetime.now(timezone.utc).isoformat(),
        "tasks":    results,
    }
    with open("gee_task_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("\n📄 Manifest written: gee_task_manifest.json")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FCD pipeline for one AOI")
    parser.add_argument("--aoi-name",  required=True)
    parser.add_argument("--aoi-asset", required=True,
                        help="GEE asset path e.g. projects/ee-athithiyan/assets/tamilnadu")
    parser.add_argument("--years",     default="2020,2025",
                        help="Comma-separated years: 2020,2025")
    parser.add_argument("--cloud-pct", type=float, default=1.0)
    parser.add_argument("--bucket",    required=True)
    args = parser.parse_args()

    selected_years = {y: DATE_WINDOWS[y] for y in args.years.split(",") if y in DATE_WINDOWS}
    if not selected_years:
        raise ValueError(f"No valid years found. Available: {list(DATE_WINDOWS.keys())}")

    run_pipeline(
        aoi_name=args.aoi_name,
        aoi_asset=args.aoi_asset,
        years=selected_years,
        cloud_pct=args.cloud_pct,
        bucket=args.bucket,
    )
