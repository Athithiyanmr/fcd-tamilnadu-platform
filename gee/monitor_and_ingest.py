"""Poll GEE task status until complete, then record COG metadata in PostGIS."""
import os
import json
import time
from datetime import datetime, timezone
import ee
from auth import initialize_ee
from sqlalchemy import create_engine, text


def wait_for_tasks(task_ids, poll_interval=60, max_wait_minutes=180):
    initialize_ee()
    pending  = set(task_ids)
    deadline = time.time() + max_wait_minutes * 60

    while pending and time.time() < deadline:
        for task_id in list(pending):
            status = ee.data.getTaskStatus(task_id)[0]
            state  = status["state"]
            name   = status.get("description", task_id)
            if state == "COMPLETED":
                print(f"✅ COMPLETED : {name}")
                pending.discard(task_id)
            elif state in ("FAILED", "CANCELLED"):
                print(f"❌ {state} : {name} — {status.get('error_message', '')}")
                pending.discard(task_id)
            else:
                print(f"⏳ {state} : {name}")
        if pending:
            time.sleep(poll_interval)

    return len(pending) == 0


def ingest_cog_metadata(db_engine, gcs_bucket, task_info):
    cog_url = f"gs://{gcs_bucket}/FCD_exports/FCD_{task_info['label']}.tif"
    year    = int(task_info["label"].split("_")[-1])

    with db_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO fcd_rasters (id, year, raster_type, cog_url, created_at)
            VALUES (gen_random_uuid(), :year, 'fcd', :cog_url, now())
            ON CONFLICT DO NOTHING;
        """), {"year": year, "cog_url": cog_url})
        conn.commit()
    print(f"📥 Ingested : {cog_url}")


if __name__ == "__main__":
    db_engine = create_engine(os.environ["DATABASE_URL"])

    with open("gee_task_manifest.json") as f:
        manifest = json.load(f)

    task_ids = [t["task_id"] for t in manifest["tasks"].values()]
    all_done = wait_for_tasks(task_ids)

    if all_done:
        for task_info in manifest["tasks"].values():
            ingest_cog_metadata(db_engine, os.environ["GCS_BUCKET"], task_info)
    else:
        print("⚠️  Some tasks did not complete within timeout window.")
