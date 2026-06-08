"""Admin units (state / district / block / forest division) endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db import get_db
from app.models import AdminUnit
from app.core.cache import cache_get, cache_set

router = APIRouter(prefix="/admin-units", tags=["Admin Units"])


@router.get("")
async def list_admin_units(
    unit_type: Optional[str] = Query(None, description="state|district|block|forest_division"),
    parent_id: Optional[str] = Query(None),
    limit:     int           = Query(200, le=1000),
    offset:    int           = Query(0, ge=0),
    db: AsyncSession         = Depends(get_db),
):
    cache_key = f"admin_units:{unit_type}:{parent_id}:{limit}:{offset}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    stmt = select(AdminUnit)
    if unit_type:
        stmt = stmt.where(AdminUnit.unit_type == unit_type)
    if parent_id:
        stmt = stmt.where(AdminUnit.parent_id == parent_id)
    stmt = stmt.order_by(AdminUnit.name).limit(limit).offset(offset)

    result = await db.execute(stmt)
    rows = [{"id": r.id, "name": r.name, "unit_type": r.unit_type,
             "parent_id": r.parent_id, "district": r.district, "state": r.state}
            for r in result.scalars().all()]

    response = {"count": len(rows), "limit": limit, "offset": offset, "results": rows}
    await cache_set(cache_key, response, ttl_seconds=600)  # 10 min cache
    return response


@router.get("/{unit_id}")
async def get_admin_unit(
    unit_id: str,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"admin_unit:{unit_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    result = await db.execute(select(AdminUnit).where(AdminUnit.id == unit_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Admin unit not found")

    data = {"id": row.id, "name": row.name, "unit_type": row.unit_type,
            "parent_id": row.parent_id, "district": row.district, "state": row.state}
    await cache_set(cache_key, data, ttl_seconds=600)
    return data
