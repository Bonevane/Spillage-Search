from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import os
import io
import json

# Authenticate and create the Drive API client
def authenticate_drive():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    service_account_info = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not service_account_info:
        raise ValueError("Service account credentials not found in environment variable.")
    creds_dict = json.loads(service_account_info)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

# List files in a folder
def list_files_in_folder(drive_service, folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

# Download a file or export if it's a Google Docs file
def download_file(drive_service, file_id, file_name, output_dir, mime_type=None):
    file_path = os.path.join(output_dir, file_name)
    
    if mime_type:  # Export Google Docs, Sheets, or Slides
        request = drive_service.files().export_media(fileId=file_id, mimeType=mime_type)
    else:  # Download binary files directly
        request = drive_service.files().get_media(fileId=file_id)

    with io.FileIO(file_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloading {file_name}: {int(status.progress() * 100)}%")

# Main function with MIME type mapping
def main():
    folder_id = '1501ty8RjYMMkTJg7TMnuRZyQ2_2yz0Lv'  # Replace with your Google Drive folder ID
    output_dir = 'indexes/test/'  # Replace with your desired download directory

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    drive_service = authenticate_drive()
    files = list_files_in_folder(drive_service, folder_id)

    # MIME type mapping for Google Docs files
    mime_type_mapping = {
        'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
        'application/vnd.google-apps.spreadsheet': 'text/csv',  # CSV
        'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # PPTX
    }

    for file in files:
        print(f"Found file: {file['name']} (ID: {file['id']})")
        mime_type = mime_type_mapping.get(file.get('mimeType'))
        
        # Determine file name based on MIME type
        if mime_type:
            extension = 'csv' if mime_type == 'text/csv' else 'exported'
            file_name = f"{file['name']}.{extension}"
        else:
            file_name = file['name']  # Use original name for binary files
        
        try:
            download_file(drive_service, file['id'], file_name, output_dir, mime_type)
        except Exception as e:
            print(f"Error downloading file {file['name']}: {e}")



