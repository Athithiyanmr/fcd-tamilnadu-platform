"""
Main FCD processing pipeline.
Downloads Sentinel-2 scenes, computes median composite,
runs FCD classification, exports COG, stores stats in PostGIS.
"""

import os
import json
import click
import numpy as np
import rasterio
from rasterio.merge import merge
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine

from sentinel_downloader import search_sentinel2, download_scene, get_scene_metadata
from fcd_algorithm import (
    run_fcd_on_stack, compute_class_areas, compute_carbon,
    compute_transition_matrix, FCDConfig
)
from cog_exporter import export_as_cog, get_aoi_bbox


@click.command()
@click.option('--aoi-name',   required=True, help='AOI name (e.g. TamilNadu, Chennai)')
@click.option('--aoi-geojson',required=True, help='Path to AOI GeoJSON boundary file')
@click.option('--year',       required=True, help='Processing year (e.g. 2025)')
@click.option('--start-date', required=True, help='Start date YYYY-MM-DD')
@click.option('--end-date',   required=True, help='End date YYYY-MM-DD')
@click.option('--cloud-pct',  default=10.0,  help='Max cloud percentage')
@click.option('--output-dir', default='/data/cogs', help='Output directory for COGs')
def run_pipeline(aoi_name, aoi_geojson, year, start_date, end_date, cloud_pct, output_dir):
    """
    Run the full FCD pipeline for one AOI and year.
    """
    print(f"\n{'='*60}")
    print(f"FCD Pipeline — {aoi_name} — {year}")
    print(f"Date range: {start_date} → {end_date}")
    print(f"{'='*60}\n")

    output_path = Path(output_dir) / aoi_name / year
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. Load AOI and compute bbox
    bbox = get_aoi_bbox(aoi_geojson)
    print(f"📍 AOI bbox: {bbox}")

    # 2. Search and download Sentinel-2 scenes
    print("\n🔍 Searching Sentinel-2 scenes...")
    items = search_sentinel2(bbox, start_date, end_date, cloud_pct)

    if not items:
        print("❌ No scenes found. Try relaxing cloud_pct or extending date range.")
        return

    print(f"\n⬇️  Downloading {len(items)} scenes...")
    scene_dir  = output_path / 'scenes'
    band_stacks = []
    scene_metas = []

    for item in items:
        paths = download_scene(item, scene_dir / item.id)
        band_stacks.append(paths)
        scene_metas.append(get_scene_metadata(item))

    # 3. Build median composite
    print("\n🔧 Building median composite...")
    green_stack = _load_and_stack([s['green'] for s in band_stacks])
    red_stack   = _load_and_stack([s['red']   for s in band_stacks])
    nir_stack   = _load_and_stack([s['nir']   for s in band_stacks])

    green_median = np.nanmedian(green_stack, axis=0).astype(np.float32) / 10000
    red_median   = np.nanmedian(red_stack,   axis=0).astype(np.float32) / 10000
    nir_median   = np.nanmedian(nir_stack,   axis=0).astype(np.float32) / 10000

    nodata_mask = (
        np.isnan(green_median) |
        np.isnan(red_median)   |
        np.isnan(nir_median)
    )

    # 4. Run FCD classification
    print("\n🌿 Classifying FCD...")
    cfg = FCDConfig()
    fcd = run_fcd_on_stack(green_median, red_median, nir_median, cfg, nodata_mask)

    # 5. Compute statistics
    class_areas  = compute_class_areas(fcd)
    carbon_stats = compute_carbon(class_areas)
    print("\n📊 Class areas:")
    for code, data in class_areas.items():
        print(f"  {data['class_name']:15s}: {data['area_ha']:>12.2f} ha")

    # 6. Export COG
    label    = f"FCD_{aoi_name}_{year}"
    cog_path = output_path / f"{label}.tif"
    with rasterio.open(band_stacks[0]['green']) as ref:
        profile = ref.profile.copy()

    export_as_cog(fcd, profile, cog_path)
    print(f"\n✅ COG exported: {cog_path}")

    # 7. Save manifest
    manifest = {
        'label':       label,
        'aoi_name':    aoi_name,
        'year':        year,
        'start_date':  start_date,
        'end_date':    end_date,
        'cloud_pct':   cloud_pct,
        'scene_count': len(items),
        'cog_path':    str(cog_path),
        'class_areas': {str(k): v for k, v in class_areas.items()},
        'carbon':      {str(k): v for k, v in carbon_stats.items()},
        'scene_log':   scene_metas,
        'processed_at': datetime.utcnow().isoformat()
    }
    manifest_path = output_path / f"{label}_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"📄 Manifest: {manifest_path}")


def _load_and_stack(paths: list) -> np.ndarray:
    """Load multiple single-band rasters and stack into 3D array."""
    arrays = []
    for path in paths:
        with rasterio.open(path) as src:
            arr = src.read(1).astype(np.float32)
            arr[arr == src.nodata] = np.nan
            arrays.append(arr)
    return np.stack(arrays, axis=0)


if __name__ == '__main__':
    run_pipeline()
