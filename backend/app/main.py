"""
FCD Tamil Nadu Platform — FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import admin_units, runs, rasters, stats, reports, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌿 FCD Tamil Nadu Platform starting...")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title="FCD Tamil Nadu API",
    description="Forest Canopy Density assessment platform for Tamil Nadu, India",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router,       tags=["health"])
app.include_router(admin_units.router,  prefix="/admin-units",  tags=["admin-units"])
app.include_router(runs.router,         prefix="/runs",          tags=["runs"])
app.include_router(rasters.router,      prefix="/rasters",       tags=["rasters"])
app.include_router(stats.router,        prefix="/stats",         tags=["stats"])
app.include_router(reports.router,      prefix="/reports",       tags=["reports"])
