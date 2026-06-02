from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from app.db import get_db
from typing import Optional

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/classes")
async def get_class_stats(
    run_id: str = Query(...),
    aoi_id: Optional[str] = Query(None),
    db=Depends(get_db),
):
    sql = """
        SELECT class_code, class_name, area_ha, percent_area
        FROM fcd_class_stats
        WHERE run_id = :run_id
    """
    params = {"run_id": run_id}
    if aoi_id:
        sql += " AND aoi_id = :aoi_id"
        params["aoi_id"] = aoi_id
    sql += " ORDER BY class_code;"
    rows = db.execute(text(sql), params).mappings().all()
    return {"run_id": run_id, "aoi_id": aoi_id, "classes": list(rows)}


@router.get("/transitions")
async def get_transitions(
    from_run_id: str = Query(...),
    to_run_id:   str = Query(...),
    aoi_id:      Optional[str] = Query(None),
    db=Depends(get_db),
):
    sql = """
        SELECT from_class_code, to_class_code, area_ha
        FROM fcd_transitions
        WHERE from_run_id = :from_run_id AND to_run_id = :to_run_id
    """
    params = {"from_run_id": from_run_id, "to_run_id": to_run_id}
    if aoi_id:
        sql += " AND aoi_id = :aoi_id"
        params["aoi_id"] = aoi_id
    sql += " ORDER BY from_class_code, to_class_code;"
    rows = db.execute(text(sql), params).mappings().all()
    return {"transitions": list(rows)}


@router.get("/carbon")
async def get_carbon_stats(
    run_id: str = Query(...),
    aoi_id: Optional[str] = Query(None),
    db=Depends(get_db),
):
    sql = """
        SELECT class_code, class_name, area_ha, coef_t_per_ha,
               carbon_t, co2eq_t
        FROM fcd_carbon_stats
        WHERE run_id = :run_id
    """
    params = {"run_id": run_id}
    if aoi_id:
        sql += " AND aoi_id = :aoi_id"
        params["aoi_id"] = aoi_id
    sql += " ORDER BY class_code;"
    rows = db.execute(text(sql), params).mappings().all()
    return {"run_id": run_id, "carbon": list(rows)}
