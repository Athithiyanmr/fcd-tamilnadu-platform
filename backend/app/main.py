"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import admin_units, runs, stats, rasters, reports, health

app = FastAPI(
    title="FCD Tamil Nadu Platform API",
    description="Forest Canopy Density WebGIS — Tamil Nadu",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Routers — all scoped under /api/v1
PREFIX = "/api/v1"
app.include_router(health.router,       prefix=PREFIX)
app.include_router(admin_units.router,  prefix=PREFIX)
app.include_router(runs.router,         prefix=PREFIX)
app.include_router(stats.router,        prefix=PREFIX)
app.include_router(rasters.router,      prefix=PREFIX)
app.include_router(reports.router,      prefix=PREFIX)
