# 🌿 Forest Canopy Density (FCD) WebGIS Platform — Tamil Nadu

> Production-ready, end-to-end FCD assessment platform for the entire state of Tamil Nadu, India.
> Built on **Sentinel-2**, **GDAL/Rasterio**, **PostGIS**, **FastAPI**, **TiTiler**, **pg_tileserv**, and **Next.js**.
> No Google Earth Engine dependency.

---

## 🏗️ Architecture

```
Sentinel-2 (Copernicus Hub / STAC)
        ↓
  [processing/]
  GDAL + Rasterio FCD pipeline
        ↓
  Cloud Storage (COG GeoTIFF)
        ↓
  [database/]
  PostGIS — boundaries, stats, carbon, scene log
        ↓
  [titiler/]   [pg_tileserv/]   [backend/]
  Raster tiles  Vector tiles     FastAPI REST
        ↓              ↓              ↓
              [frontend/]
           Next.js + MapLibre GL
                   ↓
             [reports/]
          PDF / Excel reports
```

## 📁 Project Structure

```
fcd-tamilnadu-platform/
├── processing/          # Sentinel-2 download + FCD algorithm (Python)
├── backend/             # FastAPI REST API
├── frontend/            # Next.js WebGIS dashboard
├── reports/             # PDF/Excel report generator
├── database/            # PostGIS schema and seeds
├── infra/               # Docker Compose, Nginx, Terraform
└── .github/workflows/   # CI/CD GitHub Actions
```

## 🚀 Quick Start

```bash
git clone https://github.com/Athithiyanmr/fcd-tamilnadu-platform
cd fcd-tamilnadu-platform
cp .env.example .env          # fill in your values
docker compose up --build
```

| Service        | URL                        |
|----------------|----------------------------|
| Dashboard      | http://localhost:3000      |
| API            | http://localhost:8000/docs |
| Raster tiles   | http://localhost:8080      |
| Vector tiles   | http://localhost:7800      |
| Database       | localhost:5432             |

## 🛰️ FCD Classes

| Code | Class       | Color   | Carbon coef (t/ha) |
|------|-------------|---------|---------------------|
| 0    | Other       | #000000 | 0                   |
| 1    | Water       | #3380cc | 0                   |
| 2    | High forest | #006837 | 104.58              |
| 3    | Low forest  | #3ea540 | 90.18               |
| 4    | Grassland   | #baf096 | 60.64               |
| 5    | Bare land   | #ad8855 | 0                   |

## 🔧 Requirements

- Docker + Docker Compose v2
- Python 3.11+ (for local processing)
- Node.js 20+ (for local frontend dev)
- 8 GB RAM minimum (16 GB recommended for statewide processing)

## 📄 License

MIT License — © Athithiyan M R, Auroville Consulting
