"""SQLAlchemy ORM models for the FCD platform."""
from sqlalchemy import (
    Column, String, Integer, Float, Date, DateTime, Text, func
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class FcdRun(Base):
    __tablename__ = "fcd_runs"

    id                = Column(String, primary_key=True,
                               server_default=func.gen_random_uuid().cast(String))
    run_name          = Column(String, nullable=False)
    year              = Column(Integer, nullable=False)
    start_date        = Column(Date)
    end_date          = Column(Date)
    cloud_threshold   = Column(Float, default=1.0)
    algorithm_version = Column(String, default="1.0.0")
    status            = Column(String, default="queued")
    created_by        = Column(String, default="api")
    created_at        = Column(DateTime, server_default=func.now())


class AdminUnit(Base):
    __tablename__ = "admin_units"

    id        = Column(String, primary_key=True)
    name      = Column(String, nullable=False)
    unit_type = Column(String)   # state | district | block | forest_division
    parent_id = Column(String)
    district  = Column(String)
    state     = Column(String)


class FcdRaster(Base):
    __tablename__ = "fcd_rasters"

    id           = Column(String, primary_key=True)
    run_id       = Column(String)
    aoi_id       = Column(String)
    year         = Column(Integer)
    raster_type  = Column(String)
    cog_url      = Column(Text)
    tilejson_url = Column(Text)


class FcdClassStats(Base):
    __tablename__ = "fcd_class_stats"

    id           = Column(String, primary_key=True)
    run_id       = Column(String)
    aoi_id       = Column(String)
    class_code   = Column(Integer)
    class_name   = Column(String)
    area_ha      = Column(Float)
    percent_area = Column(Float)


class FcdCarbonStats(Base):
    __tablename__ = "fcd_carbon_stats"

    id            = Column(String, primary_key=True)
    run_id        = Column(String)
    aoi_id        = Column(String)
    class_code    = Column(Integer)
    class_name    = Column(String)
    area_ha       = Column(Float)
    coef_t_per_ha = Column(Float)
    carbon_t      = Column(Float)
    co2eq_t       = Column(Float)


class FcdTransition(Base):
    __tablename__ = "fcd_transitions"

    id              = Column(String, primary_key=True)
    from_run_id     = Column(String)
    to_run_id       = Column(String)
    aoi_id          = Column(String)
    from_class_code = Column(Integer)
    to_class_code   = Column(Integer)
    area_ha         = Column(Float)


class ReportJob(Base):
    __tablename__ = "report_jobs"

    id          = Column(String, primary_key=True)
    run_id      = Column(String)
    aoi_id      = Column(String)
    report_type = Column(String)
    status      = Column(String, default="queued")
    pdf_url     = Column(Text)
    xlsx_url    = Column(Text)
    created_at  = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
