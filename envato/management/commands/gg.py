import io
import json
import os.path
import time

import requests
from django.core.management import BaseCommand
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from maxim_telegram_bot.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Path to your service account's JSON key file
        key_file = str(BASE_DIR / 'drive_storage_key.json')

        # Create credentials object using the service account key file
        credentials = service_account.Credentials.from_service_account_file(key_file)
        drive_service = build('drive', 'v3', credentials=credentials)

        file_path = str(BASE_DIR / '1GB.bin')

        # آپلود فایل با استفاده از یک فایل مستقیم
        file_metadata = {
            'name': '1GB.bin',  # Replace with the desired file name
        }
        try:
            # Step 1: Initiate a resumable upload session
            upload_request = drive_service.files().create(
                body=file_metadata,
                media_body={},
                supportsAllDrives=True
            )
            response = upload_request.execute()

            file_id = response.get('id')

            print(f"Resumable upload initiated. File ID: {file_id}")

            # Step 2: Upload the file in chunks
            chunk_size = 1024 * 1024 * 10  # Set your desired chunk size

            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break

                    # Create a MediaIoBaseUpload object for the chunk content
                    media = MediaIoBaseUpload(io.BytesIO(chunk), mimetype='application/octet-stream', resumable=True)

                    # Step 3: Resume the upload
                    upload_request = drive_service.files().update(
                        fileId=file_id,
                        media_body=media,
                        supportsAllDrives=True
                    )
                    while True:
                        try:
                            response = upload_request.execute()
                            response_message = response
                            break
                        except Exception as e:
                            response_message = str(e)
                            time.sleep(1)
                    print(response_message)

                    # Perform progress tracking or logging here
                    # For this example, printing the progress of each chunk
                    print(f"Uploaded chunk of size {len(chunk)} bytes")

            print("Resumable upload completed.")

            # (Previous code remains the same)

            print("Resumable upload completed.")

            # Check if the file is in Google Drive
            file = drive_service.files().get(fileId=file_id, supportsAllDrives=True).execute()

            if file:
                print(f"File uploaded successfully. File details: {file}")
            else:
                print("File not found in Drive.")

        except Exception as e:
            print(f"Resumable upload failed: {e}")

        # دریافت لیست تمامی فایل های موجود
        response = drive_service.files().list(fields="files(id, name)").execute()
        files = response.get('files', [])

        if files:
            for file in files:
                print(f"File found: {file['name']} - ID: {file['id']}")
                permission = {
                    'role': 'reader',
                    'type': 'anyone',
                    'allowFileDiscovery': False
                }

                # Update the permissions of the file to make it accessible to anyone with the link
                drive_service.permissions().create(fileId=file['id'], body=permission).execute()

                file_metadata = drive_service.files().get(fileId=file['id'], fields='webContentLink, webViewLink').execute()
                webViewLink = file_metadata.get('webViewLink')
                print(f'webViewLink: {webViewLink}')
                webContentLink = file_metadata.get('webContentLink')
                print(f'webContentLink: {webContentLink}')
        else:
            print("No files found in Drive.")


        # # ایجاد یک پالیسی و ایجاد لینک دانلود برای فایل
        # # Create the permission for 'Anyone with the link' with 'reader' access
        # permission = {
        #     'role': 'reader',
        #     'type': 'anyone',
        #     'allowFileDiscovery': False
        # }
        #
        # # Update the permissions of the file to make it accessible to anyone with the link
        # drive_service.permissions().create(fileId=file_id, body=permission).execute()

        # # Retrieve the file metadata to obtain the direct download link
        # file_metadata = drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
        # direct_download_link = file_metadata.get('webViewLink')
        #


        # # حذف فایل با استفاده از ایدی
        # drive_service.files().delete(fileId=file_id).execute()
        #
        # print(f"File with ID {file_id} has been deleted.")