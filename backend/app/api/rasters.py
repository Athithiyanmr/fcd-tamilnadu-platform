"""Raster catalogue and TiTiler tile URL endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import httpx
from app.db import get_db
from app.models import FcdRaster
from app.core.config import settings
from app.core.cache import cache_get, cache_set

router = APIRouter(prefix="/rasters", tags=["Rasters"])


@router.get("")
async def list_rasters(
    run_id:      Optional[str] = Query(None),
    aoi_id:      Optional[str] = Query(None),
    raster_type: Optional[str] = Query(None),
    year:        Optional[int] = Query(None),
    db: AsyncSession           = Depends(get_db),
):
    stmt = select(FcdRaster)
    if run_id:      stmt = stmt.where(FcdRaster.run_id == run_id)
    if aoi_id:      stmt = stmt.where(FcdRaster.aoi_id == aoi_id)
    if raster_type: stmt = stmt.where(FcdRaster.raster_type == raster_type)
    if year:        stmt = stmt.where(FcdRaster.year == year)
    stmt = stmt.order_by(FcdRaster.year.desc())

    result = await db.execute(stmt)
    rasters = []
    for r in result.scalars().all():
        row = {
            "id": r.id, "run_id": r.run_id, "aoi_id": r.aoi_id,
            "year": r.year, "raster_type": r.raster_type,
            "cog_url": r.cog_url, "tilejson_url": r.tilejson_url,
        }
        if r.cog_url:
            row["tile_url"] = (
                f"{settings.TITILER_URL}/cog/tiles/{{z}}/{{x}}/{{y}}.png"
                f"?url={r.cog_url}"
            )
        rasters.append(row)
    return {"rasters": rasters}


@router.get("/releases")
async def list_github_releases():
    """Proxy GitHub Releases, with 10-minute Redis cache to respect rate limits."""
    cache_key = "github:releases"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    headers = {"Accept": "application/vnd.github+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(
            f"https://api.github.com/repos/{settings.GITHUB_REPO}/releases",
            headers=headers,
        )
    res.raise_for_status()
    data = res.json()
    await cache_set(cache_key, data, ttl_seconds=600)
    return data
