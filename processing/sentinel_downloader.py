"""
Sentinel-2 L2A STAC downloader
Uses Microsoft Planetary Computer STAC (open, no credentials required)
or Copernicus Dataspace API.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

import requests
import pystac_client
from shapely.geometry import shape, mapping
from tqdm import tqdm

# Planetary Computer STAC endpoint (no credentials needed for Sentinel-2 L2A)
STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

# Required Sentinel-2 bands for FCD
FCD_BANDS = {
    'B03': 'green',   # 10 m
    'B04': 'red',     # 10 m
    'B08': 'nir',     # 10 m
}


def search_sentinel2(
    bbox: list,
    start_date: str,
    end_date: str,
    cloud_pct: float = 10.0,
    max_items: int = 50
) -> list:
    """
    Search Sentinel-2 L2A scenes via STAC.

    Parameters
    ----------
    bbox        : [min_lon, min_lat, max_lon, max_lat]
    start_date  : 'YYYY-MM-DD'
    end_date    : 'YYYY-MM-DD'
    cloud_pct   : Maximum cloud cover percentage
    max_items   : Maximum number of items to return

    Returns
    -------
    List of STAC item dictionaries
    """
    catalog = pystac_client.Client.open(STAC_URL)

    search = catalog.search(
        collections=['sentinel-2-l2a'],
        bbox=bbox,
        datetime=f"{start_date}/{end_date}",
        query={'eo:cloud_cover': {'lt': cloud_pct}},
        max_items=max_items,
        sortby='-datetime'
    )

    items = list(search.items())
    print(f"🛰️  Found {len(items)} Sentinel-2 scenes")
    for item in items:
        print(f"   {item.id} | {item.datetime.date()} | "
              f"{item.properties.get('eo:cloud_cover', 'N/A'):.1f}% cloud")
    return items


def download_band(item, band_key: str, output_dir: Path) -> Path:
    """
    Download a single band from a STAC item.
    Returns local file path.
    """
    asset   = item.assets.get(band_key)
    if asset is None:
        raise KeyError(f"Band {band_key} not found in STAC item {item.id}")

    url     = asset.href
    outfile = output_dir / f"{item.id}_{band_key}.tif"

    if outfile.exists():
        return outfile

    print(f"   ⬇️  {band_key} → {outfile.name}")
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(outfile, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    return outfile


def download_scene(item, output_dir: Path) -> dict:
    """
    Download all FCD-required bands for one scene.
    Returns dict of {band_name: local_path}.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for band_key, band_name in FCD_BANDS.items():
        paths[band_name] = download_band(item, band_key, output_dir)
    return paths


def get_scene_metadata(item) -> dict:
    """Extract scene metadata for database logging."""
    return {
        'scene_id':        item.id,
        'acquisition_time': item.datetime.isoformat(),
        'mgrs_tile':       item.properties.get('s2:mgrs_tile'),
        'cloud_pct':       item.properties.get('eo:cloud_cover'),
        'spacecraft':      item.properties.get('platform', 'Sentinel-2'),
        'stac_url':        item.get_self_href()
    }
