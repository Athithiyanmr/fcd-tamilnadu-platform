from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from app.db import get_db
from typing import Optional

router = APIRouter(prefix="/rasters", tags=["Rasters"])


@router.get("")
async def list_rasters(
    run_id:      Optional[str] = Query(None),
    aoi_id:      Optional[str] = Query(None),
    raster_type: Optional[str] = Query(None),
    db=Depends(get_db),
):
    sql    = "SELECT id, run_id, aoi_id, year, raster_type, cog_url, tilejson_url FROM fcd_rasters WHERE 1=1"
    params = {}
    if run_id:
        sql += " AND run_id = :run_id";  params["run_id"] = run_id
    if aoi_id:
        sql += " AND aoi_id = :aoi_id";  params["aoi_id"] = aoi_id
    if raster_type:
        sql += " AND raster_type = :raster_type"; params["raster_type"] = raster_type
    sql += " ORDER BY year DESC;"
    rows = db.execute(text(sql), params).mappings().all()
    return {"rasters": list(rows)}
