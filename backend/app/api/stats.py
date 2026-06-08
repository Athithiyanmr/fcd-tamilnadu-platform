"""FCD class statistics, transitions, and carbon endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db import get_db
from app.models import FcdClassStats, FcdTransition, FcdCarbonStats
from app.core.cache import cache_get, cache_set

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/classes")
async def get_class_stats(
    run_id: str              = Query(...),
    aoi_id: Optional[str]   = Query(None),
    db: AsyncSession         = Depends(get_db),
):
    cache_key = f"stats:classes:{run_id}:{aoi_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    stmt = select(FcdClassStats).where(FcdClassStats.run_id == run_id)
    if aoi_id:
        stmt = stmt.where(FcdClassStats.aoi_id == aoi_id)
    stmt = stmt.order_by(FcdClassStats.class_code)

    result = await db.execute(stmt)
    rows = [
        {"class_code": r.class_code, "class_name": r.class_name,
         "area_ha": r.area_ha, "percent_area": r.percent_area}
        for r in result.scalars().all()
    ]
    response = {"run_id": run_id, "aoi_id": aoi_id, "classes": rows}
    await cache_set(cache_key, response, ttl_seconds=300)
    return response


@router.get("/transitions")
async def get_transitions(
    from_run_id: str           = Query(...),
    to_run_id:   str           = Query(...),
    aoi_id:      Optional[str] = Query(None),
    db: AsyncSession           = Depends(get_db),
):
    cache_key = f"stats:transitions:{from_run_id}:{to_run_id}:{aoi_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    stmt = (
        select(FcdTransition)
        .where(FcdTransition.from_run_id == from_run_id)
        .where(FcdTransition.to_run_id == to_run_id)
    )
    if aoi_id:
        stmt = stmt.where(FcdTransition.aoi_id == aoi_id)
    stmt = stmt.order_by(FcdTransition.from_class_code, FcdTransition.to_class_code)

    result = await db.execute(stmt)
    rows = [
        {"from_class_code": r.from_class_code,
         "to_class_code": r.to_class_code, "area_ha": r.area_ha}
        for r in result.scalars().all()
    ]
    response = {"transitions": rows}
    await cache_set(cache_key, response, ttl_seconds=300)
    return response


@router.get("/carbon")
async def get_carbon_stats(
    run_id: str              = Query(...),
    aoi_id: Optional[str]   = Query(None),
    db: AsyncSession         = Depends(get_db),
):
    cache_key = f"stats:carbon:{run_id}:{aoi_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    stmt = select(FcdCarbonStats).where(FcdCarbonStats.run_id == run_id)
    if aoi_id:
        stmt = stmt.where(FcdCarbonStats.aoi_id == aoi_id)
    stmt = stmt.order_by(FcdCarbonStats.class_code)

    result = await db.execute(stmt)
    rows = [
        {"class_code": r.class_code, "class_name": r.class_name,
         "area_ha": r.area_ha, "coef_t_per_ha": r.coef_t_per_ha,
         "carbon_t": r.carbon_t, "co2eq_t": r.co2eq_t}
        for r in result.scalars().all()
    ]
    response = {"run_id": run_id, "carbon": rows}
    await cache_set(cache_key, response, ttl_seconds=300)
    return response
