# FCD Algorithm Reference

## Overview

Pseudo Forest Canopy Density (FCD) classification using Sentinel-2 SR Harmonized imagery.

## Indices

| Index | Formula | Band mapping (S2) |
|---|---|---|
| NDVI | (NIR − RED) / (NIR + RED) | B8, B4 |
| NDWI | (GREEN − NIR) / (GREEN + NIR) | B3, B8 |
| BI (Brightness Index) | (NIR+GREEN+RED) / (NIR+GREEN−RED) | B8, B3, B4 |
| SI (Shadow Index) | √((1−GREEN) × (1−RED)) | B3, B4 |

## Classification Rules

| Class | Code | Condition |
|---|---|---|
| Water | 1 | NDWI > 0.2 |
| High Forest | 2 | NDVI > 0.45, BI < 2, SI > 0.95 |
| Low Forest | 3 | 0.25 < NDVI ≤ 0.45, BI < 2, 0.92 < SI ≤ 0.95 |
| Grassland | 4 | NDVI > 0.25 |
| Bare Land | 5 | NDVI < 0.25, BI > 2, SI < 0.92 |
| Other | 0 | All remaining pixels |

## Carbon Coefficients

| Class | Sequestration (t C/ha) |
|---|---|
| High Forest | 104.58 |
| Low Forest | 90.18 |
| Grassland | 60.64 |
| Water / Other / Bare | 0 |

## Data Sources

- **Satellite**: Sentinel-2 MSI Level-2A Surface Reflectance (`COPERNICUS/S2_SR_HARMONIZED`)
- **Date window**: February–March (dry season, minimal cloud cover for Tamil Nadu)
- **Cloud filter**: < 1% cloudy pixel percentage per scene
- **Composite**: Median composite of all qualifying scenes
- **Resolution**: 10 m native, exported at EPSG:4326

## Limitations

- Pseudo-FCD does not use LiDAR or field canopy measurements
- Results should be validated against FSI ground-truth plots or VHR imagery
- Boundary-zone pixels may be misclassified where forest edges are heterogeneous
