
import os
import io
import config
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

class DriveClient:
    def __init__(self):
        self.creds = None
        if os.path.exists(config.GOOGLE_APPLICATION_CREDENTIALS):
            self.creds = Credentials.from_service_account_file(
                config.GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES)
        else:
            print(f"Warning: credentials file not found at {config.GOOGLE_APPLICATION_CREDENTIALS}")

    def download_file(self, file_id, local_path):
        """Tải file từ Drive về local"""
        if not self.creds:
            return False
        
        try:
            service = build('drive', 'v3', credentials=self.creds)
            request = service.files().get_media(fileId=file_id)
            
            fh = io.FileIO(local_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                # print(f"Download {int(status.progress() * 100)}%.")
                
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

    def upload_file(self, file_id, local_path):
        """Cập nhật nội dung file trên Drive"""
        if not self.creds:
            return False
            
        try:
            service = build('drive', 'v3', credentials=self.creds)
            
            media = MediaFileUpload(local_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            
            # Update file content
            service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
