from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from app.db import get_db
from typing import Optional

router = APIRouter()

@router.get("/classes")
async def get_class_stats(
    run_id: str,
    aoi_id: Optional[str] = Query(None),
    db=Depends(get_db)
):
    sql = """
        SELECT s.class_code, s.class_name, s.area_ha, s.percent_area, s.pixel_count,
               d.color_hex, d.coef_t_per_ha
        FROM fcd_class_stats s
        JOIN fcd_class_definitions d ON d.code = s.class_code
        WHERE s.run_id = :run_id
    """
    params = {'run_id': run_id}
    if aoi_id:
        sql += " AND s.aoi_id = :aoi_id"
        params['aoi_id'] = aoi_id
    sql += " ORDER BY s.class_code;"
    rows = db.execute(text(sql), params).mappings().all()
    return {'run_id': run_id, 'aoi_id': aoi_id, 'classes': list(rows)}


@router.get("/carbon")
async def get_carbon_stats(
    run_id: str,
    aoi_id: Optional[str] = Query(None),
    db=Depends(get_db)
):
    sql = """
        SELECT class_code, class_name, area_ha, coef_t_per_ha,
               carbon_t, co2eq_t
        FROM fcd_carbon_stats
        WHERE run_id = :run_id
    """
    params = {'run_id': run_id}
    if aoi_id:
        sql += " AND aoi_id = :aoi_id"
        params['aoi_id'] = aoi_id
    sql += " ORDER BY class_code;"
    rows = db.execute(text(sql), params).mappings().all()
    total_carbon = sum(float(r['carbon_t'] or 0) for r in rows)
    total_co2eq  = sum(float(r['co2eq_t']  or 0) for r in rows)
    return {'run_id': run_id, 'aoi_id': aoi_id,
            'classes': list(rows),
            'total_carbon_t': round(total_carbon, 2),
            'total_co2eq_t':  round(total_co2eq,  2)}


@router.get("/transitions")
async def get_transitions(
    from_run_id: str,
    to_run_id:   str,
    aoi_id:      Optional[str] = Query(None),
    db=Depends(get_db)
):
    sql = """
        SELECT from_class_code, to_class_code, area_ha
        FROM fcd_transitions
        WHERE from_run_id = :from_run_id AND to_run_id = :to_run_id
    """
    params = {'from_run_id': from_run_id, 'to_run_id': to_run_id}
    if aoi_id:
        sql += " AND aoi_id = :aoi_id"
        params['aoi_id'] = aoi_id
    sql += " ORDER BY from_class_code, to_class_code;"
    rows = db.execute(text(sql), params).mappings().all()
    return {'from_run_id': from_run_id, 'to_run_id': to_run_id,
            'aoi_id': aoi_id, 'transitions': list(rows)}
