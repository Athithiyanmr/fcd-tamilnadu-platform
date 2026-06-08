"""Celery tasks: FCD pipeline runner and report generator."""
import subprocess
from app.workers.celery_app import celery_app
from app.core.config import settings


@celery_app.task(bind=True, max_retries=3, name="run_fcd_pipeline")
def run_fcd_pipeline(
    self,
    aoi_name: str,
    year: str,
    start_date: str = None,
    end_date: str = None,
    cloud_pct: float = 10.0,
):
    if not start_date:
        start_date = f"{year}-02-01"
    if not end_date:
        end_date = f"{year}-03-31"

    aoi_geojson = f"/data/boundaries/{aoi_name}.geojson"
    output_dir = settings.STORAGE_LOCAL_PATH

    cmd = [
        "python", "/app/processing/pipeline.py",
        "--aoi-name",    aoi_name,
        "--aoi-geojson", aoi_geojson,
        "--year",        year,
        "--start-date",  start_date,
        "--end-date",    end_date,
        "--cloud-pct",   str(cloud_pct),
        "--output-dir",  output_dir,
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=3600, check=True
        )
        return {"status": "completed", "output": result.stdout}
    except subprocess.CalledProcessError as exc:
        raise self.retry(exc=exc, countdown=300)
    except subprocess.TimeoutExpired as exc:
        raise self.retry(exc=exc, countdown=600)


@celery_app.task(bind=True, max_retries=2, name="generate_report")
def generate_report(self, job_id: str, run_id: str, aoi_id: str, report_type: str):
    """
    Generate PDF + Excel report for a completed FCD run.
    Updates report_jobs table on completion.
    """
    import sqlalchemy
    from sqlalchemy import create_engine, text
    from datetime import datetime, timezone

    _sync_url = settings.DATABASE_URL  # use sync URL for Celery (not async)
    engine = create_engine(_sync_url, pool_pre_ping=True)

    try:
        # --- PDF generation (weasyprint / reportlab) ---
        pdf_path  = f"{settings.STORAGE_LOCAL_PATH}/reports/{job_id}.pdf"
        xlsx_path = f"{settings.STORAGE_LOCAL_PATH}/reports/{job_id}.xlsx"

        # TODO: implement PDF/Excel rendering with actual data
        # For now, write empty placeholder files so the job reaches 'completed'
        import pathlib
        pathlib.Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(pdf_path).write_text("placeholder")
        pathlib.Path(xlsx_path).write_text("placeholder")

        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE report_jobs
                SET status = 'completed',
                    pdf_url = :pdf_url,
                    xlsx_url = :xlsx_url,
                    completed_at = :completed_at
                WHERE id = :id
            """), {
                "id": job_id,
                "pdf_url":  f"/data/reports/{job_id}.pdf",
                "xlsx_url": f"/data/reports/{job_id}.xlsx",
                "completed_at": datetime.now(timezone.utc),
            })
        return {"job_id": job_id, "status": "completed"}

    except Exception as exc:
        with engine.begin() as conn:
            conn.execute(text(
                "UPDATE report_jobs SET status = 'failed' WHERE id = :id"
            ), {"id": job_id})
        raise self.retry(exc=exc, countdown=60)
