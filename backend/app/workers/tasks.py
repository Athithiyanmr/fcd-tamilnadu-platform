import os
import subprocess
from app.workers.celery_app import celery_app
from app.core.config import settings

@celery_app.task(bind=True, max_retries=3)
def run_fcd_pipeline(self, aoi_name: str, year: str,
                     start_date: str = None, end_date: str = None,
                     cloud_pct: float = 10.0):
    """
    Celery task that invokes the processing pipeline script.
    """
    if not start_date:
        start_date = f"{year}-02-01"
    if not end_date:
        end_date   = f"{year}-03-31"

    aoi_geojson = f"/data/boundaries/{aoi_name}.geojson"
    output_dir  = settings.STORAGE_LOCAL_PATH

    cmd = [
        "python", "/app/processing/pipeline.py",
        "--aoi-name",    aoi_name,
        "--aoi-geojson", aoi_geojson,
        "--year",        year,
        "--start-date",  start_date,
        "--end-date",    end_date,
        "--cloud-pct",   str(cloud_pct),
        "--output-dir",  output_dir
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if result.returncode != 0:
            raise Exception(f"Pipeline failed:\n{result.stderr}")
        return {'status': 'completed', 'output': result.stdout}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)  # retry after 5 min


@celery_app.task
def generate_report(job_id: str, run_id: str, aoi_id: str, report_type: str):
    """
    Celery task to generate PDF/Excel report.
    """
    # TODO: implement report generator
    return {'job_id': job_id, 'status': 'queued'}
