from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy import text
from app.db import get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ReportRequest(BaseModel):
    run_id:      str
    aoi_id:      str
    report_type: str  # district | block | forest_division | state

@router.post("/", status_code=202)
async def request_report(
    payload: ReportRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    sql = text("""
        INSERT INTO report_jobs (run_id, aoi_id, report_type)
        VALUES (:run_id, :aoi_id, :report_type)
        RETURNING id;
    """)
    result = db.execute(sql, payload.model_dump())
    db.commit()
    job_id = result.scalar()
    # TODO: dispatch to Celery worker
    return {"job_id": str(job_id), "status": "queued"}

@router.get("/{job_id}")
async def get_report_status(job_id: str, db=Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM report_jobs WHERE id = :id;"),
        {'id': job_id}
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Report job not found")
    return dict(row)
