from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from app.db import get_db
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter()

class RunCreate(BaseModel):
    run_name:          str
    year:              int
    start_date:        date
    end_date:          date
    cloud_threshold:   float = 1.0
    algorithm_version: str = '1.0.0'
    created_by:        Optional[str] = None

@router.get("/")
async def list_runs(db=Depends(get_db)):
    rows = db.execute(text(
        "SELECT id, run_name, year, start_date, end_date, status, created_at "
        "FROM fcd_runs ORDER BY created_at DESC;"
    )).mappings().all()
    return {"count": len(rows), "results": list(rows)}

@router.post("/", status_code=201)
async def create_run(payload: RunCreate, db=Depends(get_db)):
    sql = text("""
        INSERT INTO fcd_runs (run_name, year, start_date, end_date,
                              cloud_threshold, algorithm_version, created_by)
        VALUES (:run_name, :year, :start_date, :end_date,
                :cloud_threshold, :algorithm_version, :created_by)
        RETURNING id;
    """)
    result = db.execute(sql, payload.model_dump())
    db.commit()
    run_id = result.scalar()
    return {"id": str(run_id), "status": "queued"}

@router.get("/{run_id}")
async def get_run(run_id: str, db=Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM fcd_runs WHERE id = :id;"),
        {'id': run_id}
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    return dict(row)
