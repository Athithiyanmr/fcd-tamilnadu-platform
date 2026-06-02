from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from app.db import get_db
from typing import Optional

router = APIRouter()

@router.get("/")
async def list_admin_units(
    unit_type:  Optional[str] = Query(None, description="state|district|block|forest_division"),
    parent_id:  Optional[str] = Query(None),
    db=Depends(get_db)
):
    sql = "SELECT id, name, name_local, unit_type, parent_id, area_ha FROM admin_units WHERE 1=1"
    params = {}
    if unit_type:
        sql += " AND unit_type = :unit_type"
        params['unit_type'] = unit_type
    if parent_id:
        sql += " AND parent_id = :parent_id"
        params['parent_id'] = parent_id
    sql += " ORDER BY name;"
    rows = db.execute(text(sql), params).mappings().all()
    return {"count": len(rows), "results": list(rows)}


@router.get("/{unit_id}/geojson")
async def get_admin_unit_geojson(unit_id: str, db=Depends(get_db)):
    sql = text("""
        SELECT id, name, unit_type,
               ST_AsGeoJSON(geom)::json AS geometry
        FROM admin_units WHERE id = :unit_id;
    """)
    row = db.execute(sql, {'unit_id': unit_id}).mappings().first()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Admin unit not found")
    return {
        "type": "Feature",
        "properties": {"id": str(row['id']), "name": row['name'],
                       "unit_type": row['unit_type']},
        "geometry": row['geometry']
    }
