"""GEE authentication — service account (CI/prod) or local credentials (dev)."""
import os
import json
import ee
import google.oauth2.service_account


def initialize_ee():
    sa_key_json = os.environ.get("GEE_SERVICE_ACCOUNT_KEY")
    project_id  = os.environ.get("GEE_PROJECT_ID")
    sa_email    = os.environ.get("GEE_SERVICE_ACCOUNT_EMAIL")

    if sa_key_json:
        key_data    = json.loads(sa_key_json)
        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            key_data,
            scopes=["https://www.googleapis.com/auth/earthengine"]
        )
        ee.Initialize(credentials=credentials, project=project_id)
        print(f"✅ GEE initialized via service account: {sa_email}")
    else:
        ee.Authenticate()
        ee.Initialize(project=project_id or "your-dev-project")
        print("✅ GEE initialized via local credentials")
