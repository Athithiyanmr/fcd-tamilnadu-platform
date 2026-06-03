# Deployment Guide

## Architecture Overview

```
GEE (Sentinel-2 processing)
  └─→ Google Drive (GeoTIFF export)
        └─→ GitHub Actions (download + upload)
              └─→ GitHub Releases (free GeoTIFF storage)
                    └─→ TiTiler (serves COG tiles via HTTPS URL)
                    └─→ PostGIS (stores release URLs + stats)
                          └─→ FastAPI → Next.js WebGIS dashboard
```

**No GCS / S3 required.** GeoTIFFs are stored as GitHub Release assets (free, public HTTPS).

---

## Prerequisites

- Docker Desktop installed and running
- Git
- Google Cloud project with Earth Engine API enabled
- GEE service account (for GitHub Actions)

---

## Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/Athithiyanmr/fcd-tamilnadu-platform.git
cd fcd-tamilnadu-platform

# 2. Fix macOS xattr issues if project is on external drive
find . -name "._*" -delete
xattr -rc .

# 3. Create .env
cp .env.example .env
# Edit .env — minimum required: GEE_PROJECT_ID, DATABASE_URL, REDIS_URL

# 4. Start all services
cd infra
docker compose up -d --build

# 5. Verify
curl http://localhost:8000/health   # → {"status":"ok"}
curl http://localhost:8080/healthz  # → TiTiler health
open http://localhost:3000          # Frontend
open http://localhost:8000/docs     # FastAPI Swagger UI
```

---

## Service URLs

| Service | Port | URL |
|---|---|---|
| FastAPI backend | 8000 | http://localhost:8000/docs |
| TiTiler raster tiles | 8080 | http://localhost:8080 |
| pg_tileserv vector tiles | 7800 | http://localhost:7800 |
| Next.js frontend | 3000 | http://localhost:3000 |
| PostgreSQL/PostGIS | 5432 | internal |
| Redis | 6379 | internal |

---

## GitHub Actions Setup

### Add these secrets
Go to: **GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|---|---|
| `GEE_SERVICE_ACCOUNT_KEY` | Full JSON content of your service account key |
| `GEE_SERVICE_ACCOUNT_EMAIL` | `fcd-gee-runner@PROJECT.iam.gserviceaccount.com` |
| `GEE_PROJECT_ID` | Your Google Cloud project ID (e.g. `ee-athithiyan`) |
| `DATABASE_URL` | PostgreSQL connection string for your production DB |

> **No `GCS_BUCKET` needed.** GeoTIFFs go to GitHub Releases.
> `GITHUB_TOKEN` is automatically provided by Actions — no secret needed.

---

## Workflows

| Workflow | Trigger | What it does |
|---|---|---|
| `fcd_annual_run.yml` | Cron 1 March / manual | GEE → Drive → GitHub Release → PostGIS |
| `fcd_ingest.yml` | Manual | Re-ingest a release tag's URLs into PostGIS |
| `fcd_zonal_stats.yml` | Manual | Compute district/block/division stats |
| `backend_ci.yml` | Push to main | pytest + Docker build check |

---

## Manual Pipeline Run

1. Go to **Actions → FCD Annual Processing — Tamil Nadu**
2. Click **Run workflow**
3. Set:
   - `aoi_name`: `TamilNadu`
   - `aoi_asset`: `projects/ee-athithiyan/assets/tamilnadu_boundary`
   - `years`: `2025`
4. Click **Run workflow**
5. Monitor progress in the Actions log
6. When complete, check **Releases** for the new `fcd-2025` release with `.tif` assets

---

## TiTiler — Serving GitHub Release GeoTIFFs

TiTiler can serve any public COG via URL:

```
http://localhost:8080/cog/tiles/{z}/{x}/{y}.png
  ?url=https://github.com/Athithiyanmr/fcd-tamilnadu-platform/releases/download/fcd-2025/FCD_TamilNadu_2025.tif
  &colormap_name=greens
```

Get TileJSON:
```
http://localhost:8080/cog/tilejson.json
  ?url=https://github.com/.../FCD_TamilNadu_2025.tif
```
