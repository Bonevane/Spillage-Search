from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import os
import io
import json
import base64

credentials_base64 = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAic2lsdmVyLXRyZWF0LTQ0NTQyMC1qNSIsCiAgInByaXZhdGVfa2V5X2lkIjogIjRkMWQwNTA5YTdmNmE5NGQ1Mzg2MGU1MzNjODcwOTQ3MWVlYjJhNTEiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRRFBTZHNZMGhLS055dTBcblZ2bjVuQUFHRDBJRGNBZUpuUjZMWVluNURZdDVJQ1E5bjA0WitVMnBaUVFDd1NLNTNKbTJKUXJOa1JEdGV6Nk9cbkprR0poS2d0SmtpNkFObWdZRndHWE1ZaUV1MnVRWWJxS3NmdldudWswejBGb2NhVUZtRTFXSzc5ZU1LSjBGT3lcbjh6Ulg0Q20xcElVYjZwS0NYaDNnMlFpbk85YWp1QWY1cE9QSit6U3RKa3NDZk9ZVDBQeGlFM2hQMDRXL3UyQ29cbmkxa0JVSW5jZUcrUldrWUVRemZBWkFuSi9EVXpZbWYwTkFLTDBxbEVtSEdMODU4dDMrUnFCY0grNk8wSW5ESENcbmw2WXdVK09qZGYwUlo1NjFmUG9aalBDcmQ2YjhxZHg3QmVwNm5LRG55cHBhcGQ5QWdXZ1hHRHhvUEVsSnhYOWtcbk9GZ0NvUkNWQWdNQkFBRUNnZ0VBRFM5RTdOUzcwaWZGTTJETzRKWVFHRktUSDlYWjNPSnVCVzZNVUplUWRnRlpcbjNNT0x1N0kwUXVDR2UwaGVsWlRYQUJObUZ3SXhvZkZUWHNaSEorQ1VzOTU2Qkw2MkdQSFlHSjJCQ3J6S2VtbDNcbmsrQnB2Q3Mwcnh5eWhtK3VTbEFNR2RFTXZGbVlnaHlLbmxqQ3pRNFlpUkd3VjhDNVZlcDNtd3dpOVVRa21HQW9cbmJSR080WkwwVm94SHJWRXY3MU5tU0ZsdDBNK0ZKc3liT2E1ZndFeWxHdWVQaEZxNTluNit1eGhxMXJOc1lGaFFcblpWcmUxV3JCUzZYVnZKRzkxNUlmM3huNTVqaFVpclFXUlM2YlVJdXU5VjM0TWkxdnNKZzlyOThkdmx5WWpJbk5cbkhFUndyVTFRY3lFdU1DL1ByYWRPekZ2OHRpVjNkSDdsREZxVWdXazU5d0tCZ1FEc2lpVEdDcXhHZFYvWGZJNjhcbk04eThkdURiK3ovVE04ZlRzNGJ0bi9aZi9WY1N2SWdGbmtSNUlKeit5aGJEc3I1d2Ywdy9YQm93TDlIVk0wZVpcbktQNGFsNjlNMDlPclFnb1k1Tk9TWHduT2t2M2N3eWgvc1NlOGV5Z25JMUZSVzVBNTBhZ21GeHZ6Mk0yOEkvVnpcbmt2OUNicFZBcDhnTHlXN1N0Q1lySk52QWZ3S0JnUURnVjZSNXpCZWlNRDZ2SGxYQWRYbXFKZDFqMksrMFB5TjdcbllCV3VQNVRaZXA0b210VWVWTkZCSXZKUC9XU1lIV0tyZW5wQVk4c1pTR3FIY081eWRJaG53dzRrMC93KzZ2c05cbnRBc2FDcVl6bFY4UTJld1pWWllxNlZ3K1p1OW44K3k3dnB5d0t6KzNZUjZnS2ZvSVNIUkZUbTZYQnJyemVHVVNcbnZhcUV6MnFrNndLQmdRRFVXTWZlaWlKU05uak42R0h6RHNXVHcxemwzMDVTK2o5QURBRHJQaGxkM3Y3V01TNGpcbmJRdW5lZUcyMGhGUnFodFF2dGJpWW5xWUc3WFNJZkQ2ekZRaDUxNVdLQ3Z6cUp1TDhaRUY3QS9QeFNIbGw4VzVcbnJINHh0Slk5WEhWYUJrc1p2TitwSWtIVHpTUVU3R3NqVUNtYnA4NlJkbzRlRnIxSXByVkZNaGVkWFFLQmdRQ3lcbkFiaTNEOUw4MVMwWHhJa2tJZEo4eUhpblBnc0VpVWk5SDF0MG5HeWVONllBOEFJRWhDWlplY0lzNkJHR2hXS0NcblQ3ZHJHZ1BRTnQ2WVEycGdGTWtiRS9GSUZaQkQyQzJHRFFMMkVkY1lmUUFtbmRPeHNuQnA4aXBJTldMbTUreENcbmVCZFp6YWRMK1ZyVW1Sb1VzbkRYZ1VsTXVvRmlxSGdDYTg0K2ZWblFLd0tCZ0NWdGkyaGpSZVBUYnpHd3FzT2hcbjdCdlN5c25HMWJqRFY2MHJHUkZ6QXE4NGRQbkd2Rys1bHdGaDlBdlpXZEtpWm1RSGJ4Y3FIVVVJeGhYUXlrWk9cbkgxeUxJaFpxbkJSOVNjWVRWOVAxbXZwRGdjVkVyZURMODM3ZHh2NGU1SDFLMk92S1dWS1NPcWh0QjN4TlZTaDNcbmlGSzh6MzlMYVlrSXQ4d3NtbFhXbkNBSVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImJhcnJlbC1yZXRyaWV2YWxAc2lsdmVyLXRyZWF0LTQ0NTQyMC1qNS5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgImNsaWVudF9pZCI6ICIxMTU5OTcyMDQzNjQyNTgzNjEzNDYiLAogICJhdXRoX3VyaSI6ICJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20vby9vYXV0aDIvYXV0aCIsCiAgInRva2VuX3VyaSI6ICJodHRwczovL29hdXRoMi5nb29nbGVhcGlzLmNvbS90b2tlbiIsCiAgImF1dGhfcHJvdmlkZXJfeDUwOV9jZXJ0X3VybCI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9vYXV0aDIvdjEvY2VydHMiLAogICJjbGllbnRfeDUwOV9jZXJ0X3VybCI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9yb2JvdC92MS9tZXRhZGF0YS94NTA5L2JhcnJlbC1yZXRyaWV2YWwlNDBzaWx2ZXItdHJlYXQtNDQ1NDIwLWo1LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIgp9Cg=="

# Authenticate and create the Drive API client
def authenticate_drive():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    decoded_credentials = base64.b64decode(credentials_base64)
    creds_dict = json.loads(decoded_credentials)
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
    output_dir = 'indexes/inverted/'  # Replace with your desired download directory

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



