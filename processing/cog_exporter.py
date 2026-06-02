"""
Export FCD rasters as Cloud Optimized GeoTIFF (COG)
using rio-cogeo.
"""

import json
import numpy as np
import rasterio
from rasterio.crs import CRS
from pathlib import Path
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles
from shapely.geometry import box, mapping


def export_as_cog(array: np.ndarray, src_profile: dict, output_path: Path,
                  nodata: int = 255) -> Path:
    """
    Write a uint8 array as a Cloud Optimized GeoTIFF.
    """
    tmp_path = output_path.with_suffix('.tmp.tif')

    profile = src_profile.copy()
    profile.update({
        'dtype':   'uint8',
        'count':   1,
        'nodata':  nodata,
        'crs':     CRS.from_epsg(4326),
        'compress': 'deflate'
    })

    with rasterio.open(tmp_path, 'w', **profile) as dst:
        dst.write(array.astype(np.uint8), 1)

    # Convert to COG
    cog_profile = cog_profiles.get('deflate')
    cog_translate(
        str(tmp_path),
        str(output_path),
        cog_profile,
        overview_resampling='nearest',
        add_mask=True,
        quiet=False
    )

    tmp_path.unlink(missing_ok=True)
    print(f"✅ COG written: {output_path}")
    return output_path


def get_aoi_bbox(geojson_path: str) -> list:
    """
    Read a GeoJSON file and return its [min_lon, min_lat, max_lon, max_lat] bbox.
    """
    with open(geojson_path) as f:
        geojson = json.load(f)

    from shapely.geometry import shape
    if geojson['type'] == 'FeatureCollection':
        geoms = [shape(f['geometry']) for f in geojson['features']]
    elif geojson['type'] == 'Feature':
        geoms = [shape(geojson['geometry'])]
    else:
        geoms = [shape(geojson)]

    from shapely.ops import unary_union
    union = unary_union(geoms)
    return list(union.bounds)  # (minx, miny, maxx, maxy)
