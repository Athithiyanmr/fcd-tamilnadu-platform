from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from app.db import get_db
from typing import Optional
import os

router = APIRouter(prefix="/rasters", tags=["Rasters"])

GITHUB_REPO = os.environ.get("GITHUB_REPO", "Athithiyanmr/fcd-tamilnadu-platform")


@router.get("")
async def list_rasters(
    run_id:      Optional[str] = Query(None),
    aoi_id:      Optional[str] = Query(None),
    raster_type: Optional[str] = Query(None),
    year:        Optional[int] = Query(None),
    db=Depends(get_db),
):
    sql    = "SELECT id, run_id, aoi_id, year, raster_type, cog_url, tilejson_url FROM fcd_rasters WHERE 1=1"
    params = {}
    if run_id:
        sql += " AND run_id = :run_id";          params["run_id"] = run_id
    if aoi_id:
        sql += " AND aoi_id = :aoi_id";          params["aoi_id"] = aoi_id
    if raster_type:
        sql += " AND raster_type = :raster_type"; params["raster_type"] = raster_type
    if year:
        sql += " AND year = :year";               params["year"] = year
    sql += " ORDER BY year DESC;"
    rows = db.execute(text(sql), params).mappings().all()

    # Build TiTiler tile URL from GitHub Release download URL
    result = []
    for r in rows:
        row = dict(r)
        if row.get("cog_url"):
            row["tile_url"] = (
                f"http://localhost:8080/cog/tiles/{{z}}/{{x}}/{{y}}.png"
                f"?url={row['cog_url']}"
            )
        result.append(row)
    return {"rasters": result}


@router.get("/releases")
async def list_github_releases():
    """Proxy GitHub Releases API to list available FCD release assets."""
    import httpx
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/releases",
            headers={"Accept": "application/vnd.github+json"},
        )
    return res.json()
