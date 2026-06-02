"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import admin_units, runs, stats, rasters, reports

app = FastAPI(
    title="FCD Tamil Nadu Platform API",
    description="Forest Canopy Density WebGIS — Tamil Nadu",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_units.router)
app.include_router(runs.router)
app.include_router(stats.router)
app.include_router(rasters.router)
app.include_router(reports.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "FCD Tamil Nadu Platform"}
