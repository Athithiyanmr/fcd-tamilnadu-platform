"""FCD processing run endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.db import get_db
from app.models import FcdRun
from app.core.auth import require_auth
from app.workers.tasks import run_fcd_pipeline

router = APIRouter(prefix="/runs", tags=["Runs"])


class RunCreate(BaseModel):
    run_name:          str
    year:              int
    start_date:        date
    end_date:          date
    cloud_threshold:   float = 1.0
    algorithm_version: str   = "1.0.0"
    created_by:        str   = "api"


@router.get("")
async def list_runs(
    year:   Optional[int] = Query(None),
    status: Optional[str] = Query(None, description="queued|running|completed|failed"),
    limit:  int           = Query(50, le=200),
    offset: int           = Query(0, ge=0),
    db: AsyncSession      = Depends(get_db),
):
    stmt = select(FcdRun)
    if year:
        stmt = stmt.where(FcdRun.year == year)
    if status:
        stmt = stmt.where(FcdRun.status == status)
    stmt = stmt.order_by(FcdRun.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    rows = result.scalars().all()
    return {
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "runs": [
            {"id": r.id, "run_name": r.run_name, "year": r.year,
             "start_date": r.start_date, "end_date": r.end_date,
             "status": r.status, "created_at": r.created_at}
            for r in rows
        ],
    }


@router.post("", status_code=201)
async def create_run(
    payload: RunCreate,
    db: AsyncSession = Depends(get_db),
    _auth: dict      = Depends(require_auth),
):
    run = FcdRun(**payload.model_dump())
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Enqueue the processing pipeline task
    run_fcd_pipeline.delay(
        aoi_name=payload.run_name,
        year=str(payload.year),
        start_date=str(payload.start_date),
        end_date=str(payload.end_date),
        cloud_pct=payload.cloud_threshold,
    )

    return {"id": run.id, "status": run.status}


@router.get("/{run_id}")
async def get_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FcdRun).where(FcdRun.id == run_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "id": row.id, "run_name": row.run_name, "year": row.year,
        "start_date": row.start_date, "end_date": row.end_date,
        "cloud_threshold": row.cloud_threshold,
        "algorithm_version": row.algorithm_version,
        "status": row.status, "created_by": row.created_by,
        "created_at": row.created_at,
    }
