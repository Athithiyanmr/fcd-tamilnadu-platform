"""
Forest Canopy Density (FCD) Algorithm
Inputs : Sentinel-2 L2A bands (10 m)
Outputs: Classified FCD raster (uint8, COG)

Classes
-------
0 - Other / NoData
1 - Water         (NDWI > 0.2)
2 - High forest   (NDVI > 0.45, BI < 2, SI > 0.95)
3 - Low forest    (NDVI 0.25-0.45, BI < 2, SI 0.92-0.95)
4 - Grassland     (NDVI > 0.25)
5 - Bare land     (NDVI < 0.25, BI > 2, SI < 0.92)
"""

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FCDConfig:
    detect_water: bool  = True
    ndwi_hi:      float = 0.20
    bi_hi:        float = 2.00
    ndvi_lo:      float = 0.25
    ndvi_hi:      float = 0.45
    si_lo:        float = 0.92
    si_hi:        float = 0.95
    nodata:       int   = 255


CLASS_CODES  = [0, 1, 2, 3, 4, 5]
CLASS_NAMES  = ['Other', 'Water', 'High forest', 'Low forest', 'Grassland', 'Bare land']
CLASS_COLORS = ['#000000', '#3380cc', '#006837', '#3ea540', '#baf096', '#ad8855']
SEQ_COEF     = {0: 0, 1: 0, 2: 104.58, 3: 90.18, 4: 60.64, 5: 0}


def compute_indices(green: np.ndarray, red: np.ndarray, nir: np.ndarray):
    """
    Compute spectral indices from Sentinel-2 surface reflectance bands.
    All input arrays must be float32 in range [0, 1].
    Returns NDVI, NDWI, BI, SI as float32 arrays.
    """
    eps = 1e-10  # avoid division by zero

    ndvi = (nir - red)  / (nir + red  + eps)
    ndwi = (green - nir) / (green + nir + eps)
    bi   = (nir + green + red) / (nir + green - red + eps)
    si   = np.sqrt(np.clip((1 - green) * (1 - red), 0, None))

    return (
        ndvi.astype(np.float32),
        ndwi.astype(np.float32),
        bi.astype(np.float32),
        si.astype(np.float32)
    )


def classify_fcd(ndvi, ndwi, bi, si, cfg: FCDConfig = FCDConfig()) -> np.ndarray:
    """
    Apply FCD classification logic.
    Returns uint8 raster with class codes 0-5.
    """
    out = np.zeros(ndvi.shape, dtype=np.uint8)

    # Priority order: water → high forest → low forest → grassland → bare → other
    bare_mask      = (ndvi < cfg.ndvi_lo)  & (bi > cfg.bi_hi) & (si < cfg.si_lo)
    grass_mask     = (ndvi > cfg.ndvi_lo)
    low_forest     = (ndvi > cfg.ndvi_lo)  & (ndvi <= cfg.ndvi_hi) & \
                     (bi < cfg.bi_hi)      & (si > cfg.si_lo) & (si <= cfg.si_hi)
    high_forest    = (ndvi > cfg.ndvi_hi)  & (bi < cfg.bi_hi) & (si > cfg.si_hi)
    water_mask     = (ndwi > cfg.ndwi_hi)

    out[bare_mask]   = 5
    out[grass_mask]  = 4
    out[low_forest]  = 3
    out[high_forest] = 2
    if cfg.detect_water:
        out[water_mask] = 1

    return out


def run_fcd_on_stack(
    green: np.ndarray,
    red:   np.ndarray,
    nir:   np.ndarray,
    cfg:   FCDConfig = FCDConfig(),
    nodata_mask: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Full pipeline: reflectance arrays → classified FCD array.
    Applies nodata mask if provided.
    """
    ndvi, ndwi, bi, si = compute_indices(green, red, nir)
    fcd = classify_fcd(ndvi, ndwi, bi, si, cfg)

    if nodata_mask is not None:
        fcd[nodata_mask] = cfg.nodata

    return fcd


def compute_class_areas(fcd_array: np.ndarray, pixel_area_ha: float = 0.01) -> dict:
    """
    Compute area in hectares per FCD class.
    At 10 m resolution, pixel_area_ha = 0.01 ha.
    """
    result = {}
    for code, name in zip(CLASS_CODES, CLASS_NAMES):
        px_count = int(np.sum(fcd_array == code))
        result[code] = {
            'class_name':  name,
            'pixel_count': px_count,
            'area_ha':     round(px_count * pixel_area_ha, 4)
        }
    return result


def compute_carbon(class_areas: dict) -> dict:
    """
    Compute carbon sequestration and CO2-equivalent per class.
    """
    result = {}
    for code, data in class_areas.items():
        coef         = SEQ_COEF.get(code, 0)
        carbon_t     = round(data['area_ha'] * coef, 4)
        co2eq_t      = round(carbon_t * 3.67, 4)
        result[code] = {**data, 'coef_t_per_ha': coef,
                        'carbon_t': carbon_t, 'co2eq_t': co2eq_t}
    return result


def compute_transition_matrix(fcd_t1: np.ndarray, fcd_t2: np.ndarray,
                               pixel_area_ha: float = 0.01) -> dict:
    """
    Compute class transition matrix (ha) between two FCD maps.
    Returns dict: {(from_code, to_code): area_ha}
    """
    matrix = {}
    for fr in CLASS_CODES:
        for to in CLASS_CODES:
            mask = (fcd_t1 == fr) & (fcd_t2 == to)
            px   = int(np.sum(mask))
            if px > 0:
                matrix[(fr, to)] = round(px * pixel_area_ha, 4)
    return matrix
