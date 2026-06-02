# Deployment Guide

## Prerequisites

- Docker & Docker Compose installed
- Google Cloud project with Earth Engine API enabled
- GEE service account with `roles/earthengine.writer` and `roles/storage.objectAdmin`
- Google Cloud Storage bucket for COG exports
- PostgreSQL/PostGIS (local via Docker Compose or managed, e.g. Cloud SQL / Supabase)

## Quick Start (Local)

```bash
# 1. Clone the repo
git clone https://github.com/Athithiyanmr/fcd-tamilnadu-platform.git
cd fcd-tamilnadu-platform

# 2. Copy and fill in environment variables
cp .env.example .env
# Edit .env with your GEE_PROJECT_ID, GCS_BUCKET, etc.

# 3. Start all services
cd infra
docker compose up -d --build

# 4. Verify services
curl http://localhost:8000/health   # FastAPI
curl http://localhost:8080/healthz  # TiTiler
curl http://localhost:7800/         # pg_tileserv
open http://localhost:3000          # Frontend
```

## GitHub Actions Setup

1. Go to **Settings → Secrets and variables → Actions**
2. Add the following secrets:

| Secret | Description |
|---|---|
| `GEE_SERVICE_ACCOUNT_KEY` | Full JSON of your service account key file |
| `GEE_SERVICE_ACCOUNT_EMAIL` | `fcd-gee-runner@PROJECT.iam.gserviceaccount.com` |
| `GEE_PROJECT_ID` | Google Cloud project ID |
| `GCS_BUCKET` | Cloud Storage bucket name for COG exports |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/fcd` |

## Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `fcd_annual_run.yml` | Cron: 1 March / manual | Run FCD pipeline, start GEE export tasks |
| `fcd_ingest.yml` | Cron every 2 hrs in March / manual | Poll GEE tasks, ingest COG URLs to PostGIS |
| `fcd_zonal_stats.yml` | Manual with run_id + admin_level | Compute district/block/division stats |
| `backend_ci.yml` | Push to main/develop | Run FastAPI tests + Docker build check |

## Service Ports

| Service | Port | URL |
|---|---|---|
| FastAPI backend | 8000 | http://localhost:8000/docs |
| TiTiler raster tiles | 8080 | http://localhost:8080 |
| pg_tileserv vector tiles | 7800 | http://localhost:7800 |
| Next.js frontend | 3000 | http://localhost:3000 |
| PostgreSQL/PostGIS | 5432 | — |
| Redis | 6379 | — |

## Cloud Deployment (GCP)

- Use **Cloud Run** for API and TiTiler (stateless)
- Use **Cloud SQL** (PostgreSQL) with PostGIS extension for the database
- Use **Cloud Storage** for COG rasters
- Use **Artifact Registry** for Docker images
- Use **Cloud Scheduler** instead of GitHub Actions cron for production scheduling
