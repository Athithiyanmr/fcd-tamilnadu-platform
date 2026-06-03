"""
Download GeoTIFF exports from Google Drive to local ./outputs/ folder.
Runs inside GitHub Actions after GEE tasks complete.
Requires: GDRIVE_CREDENTIALS_JSON secret (OAuth2 service account with Drive access).
"""
import os
import json
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

FOLDER_NAME = "FCD_exports"
OUTPUT_DIR  = Path("./outputs")
SCOPES      = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    key_data    = json.loads(os.environ["GEE_SERVICE_ACCOUNT_KEY"])
    credentials = Credentials.from_service_account_info(key_data, scopes=SCOPES)
    return build("drive", "v3", credentials=credentials)


def find_folder_id(service, folder_name):
    res = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)",
    ).execute()
    files = res.get("files", [])
    if not files:
        raise FileNotFoundError(f"Drive folder '{folder_name}' not found.")
    return files[0]["id"]


def download_tiffs(service, folder_id, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    res = service.files().list(
        q=f"'{folder_id}' in parents and name contains 'FCD_' and name contains '.tif' and trashed=false",
        fields="files(id, name)",
    ).execute()
    files = res.get("files", [])
    if not files:
        print("⚠️  No FCD GeoTIFFs found in Drive folder.")
        return []

    downloaded = []
    for f in files:
        dest = output_dir / f["name"]
        print(f"⬇️  Downloading : {f['name']}")
        request = service.files().get_media(fileId=f["id"])
        with open(dest, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request, chunksize=50 * 1024 * 1024)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        print(f"✅  Saved : {dest}")
        downloaded.append(str(dest))
    return downloaded


if __name__ == "__main__":
    service   = get_drive_service()
    folder_id = find_folder_id(service, FOLDER_NAME)
    files     = download_tiffs(service, folder_id, OUTPUT_DIR)
    print(f"\n📦 Downloaded {len(files)} file(s):")
    for f in files:
        print(f"   {f}")
