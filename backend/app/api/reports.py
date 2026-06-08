"""Report generation job endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db import get_db
from app.models import ReportJob
from app.core.auth import require_auth
from app.workers.tasks import generate_report

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportRequest(BaseModel):
    run_id:      str
    aoi_id:      str
    report_type: str  # state | district | block | forest_division


@router.post("", status_code=202)
async def create_report(
    payload: ReportRequest,
    db: AsyncSession = Depends(get_db),
    _auth: dict      = Depends(require_auth),
):
    job = ReportJob(
        run_id=payload.run_id,
        aoi_id=payload.aoi_id,
        report_type=payload.report_type,
        status="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Enqueue Celery task
    generate_report.delay(
        job_id=str(job.id),
        run_id=payload.run_id,
        aoi_id=payload.aoi_id,
        report_type=payload.report_type,
    )

    return {"job_id": job.id, "status": "queued",
            "message": "Report generation queued."}


@router.get("/{job_id}")
async def get_report(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ReportJob).where(ReportJob.id == job_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Report job not found")
    return {
        "id": row.id, "run_id": row.run_id, "aoi_id": row.aoi_id,
        "report_type": row.report_type, "status": row.status,
        "pdf_url": row.pdf_url, "xlsx_url": row.xlsx_url,
        "created_at": row.created_at, "completed_at": row.completed_at,
    }
