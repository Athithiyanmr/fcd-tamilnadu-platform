from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.db import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportRequest(BaseModel):
    run_id:      str
    aoi_id:      str
    report_type: str   # state | district | block | forest_division


@router.post("", status_code=202)
async def create_report(payload: ReportRequest, db=Depends(get_db)):
    result = db.execute(text("""
        INSERT INTO report_jobs (run_id, aoi_id, report_type, status)
        VALUES (:run_id, :aoi_id, :report_type, 'queued')
        RETURNING id;
    """), payload.model_dump())
    db.commit()
    job_id = result.scalar_one()
    # TODO: enqueue to Celery worker
    return {"job_id": job_id, "status": "queued",
            "message": "Report generation queued."}


@router.get("/{job_id}")
async def get_report(job_id: str, db=Depends(get_db)):
    row = db.execute(text(
        "SELECT id, run_id, aoi_id, report_type, status, pdf_url, xlsx_url, completed_at "
        "FROM report_jobs WHERE id = :id"
    ), {"id": job_id}).mappings().first()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report job not found")
    return dict(row)
