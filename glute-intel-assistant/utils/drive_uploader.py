# utils/drive_uploader.py

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

# Setup once per session
def authenticate_drive():
    gauth = GoogleAuth()

    # Use local webserver for authentication
    gauth.LoadCredentialsFile("token.json")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("token.json")
    return GoogleDrive(gauth)

def create_drive_folder_if_missing(drive, folder_name, parent_id=None):
    """Checks if folder exists, creates it if not. Returns folder ID."""
    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        return file_list[0]['id']
    
    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [{"id": parent_id}]
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder['id']

def upload_image_to_drive(drive, file, filename, session_folder_id):
    """Uploads image file to Drive inside given session folder."""
    upload = drive.CreateFile({
        'title': filename,
        'parents': [{'id': session_folder_id}]
    })
    file.seek(0)  # reset pointer
    upload.SetContentFile(file.name)
    upload.Upload()
    return upload['alternateLink']
