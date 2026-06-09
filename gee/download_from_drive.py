"""
Downloads exported GeoTIFFs from Google Drive folder to gee/outputs/.
Called by fcd_annual_run.yml after run_fcd_pipeline.py completes.
"""
import os, io, json, tempfile
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SA_KEY_JSON  = os.environ["GEE_SERVICE_ACCOUNT_KEY"]
DRIVE_FOLDER = "fcd_tamilnadu_exports"
OUTPUT_DIR   = Path("outputs")
SCOPES       = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    key = json.loads(SA_KEY_JSON)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(key, f)
        keyfile = f.name
    creds = service_account.Credentials.from_service_account_file(keyfile, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def list_tif_files(service, folder_name: str) -> list:
    q = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    folders = (
        service.files()
        .list(q=q, fields="files(id,name)")
        .execute()
        .get("files", [])
    )
    if not folders:
        print(f"\u26a0\ufe0f  Drive folder '{folder_name}' not found.")
        return []
    folder_id = folders[0]["id"]

    q2 = f"'{folder_id}' in parents and name contains '.tif' and trashed=false"
    files = (
        service.files()
        .list(q=q2, fields="files(id,name,size)")
        .execute()
        .get("files", [])
    )
    return files


def download_file(service, file_id: str, file_name: str, dest_dir: Path) -> None:
    dest = dest_dir / file_name
    if dest.exists():
        print(f"  \u23ed\ufe0f  Already exists: {file_name}")
        return
    request    = service.files().get_media(fileId=file_id)
    fh         = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    dest.write_bytes(fh.getvalue())
    size_mb = dest.stat().st_size / 1e6
    print(f"  \u2705 Downloaded: {file_name} ({size_mb:.1f} MB)")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    svc   = get_drive_service()
    files = list_tif_files(svc, DRIVE_FOLDER)
    if not files:
        print("No .tif files found in Drive. Exiting.")
        return
    print(f"\n\U0001f4e5 Downloading {len(files)} file(s) \u2192 {OUTPUT_DIR}/")
    for f in files:
        download_file(svc, f["id"], f["name"], OUTPUT_DIR)
    print(f"\n\u2705 All files downloaded to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
