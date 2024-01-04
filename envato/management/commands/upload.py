import os
import time
import paramiko
from django.core.management import BaseCommand

from core.models import File
from custom_logs.models import custom_log
from maxim_telegram_bot.settings import DOWNLOAD_FOLDER


class Command(BaseCommand):
    def handle(self, *args, **options):
        test_upload()


def create_remote_directory(sftp, remote_filepath):
    remote_path, _ = os.path.split(remote_filepath)
    try:
        sftp.stat(remote_path)
    except FileNotFoundError:
        sftp.mkdir(remote_path)
        

def are_files_similar(sftp, remote_filepath, local_filepath):
    try:
        remote_file_size = sftp.stat(remote_filepath).st_size

        local_file_size = os.path.getsize(local_filepath)
        if remote_file_size != local_file_size:
            print(f"File sizes differ. Deleting remote file: {remote_filepath}")
            sftp.remove(remote_filepath)
            return False
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking file similarity: {e}")
        return False


def upload_file_to_remote(local_filepath, remote_filepath, ssh_host, ssh_port, ssh_username, ssh_password):
    try:
        with paramiko.Transport((ssh_host, ssh_port)) as transport:
            transport.connect(username=ssh_username, password=ssh_password)
            with paramiko.SFTPClient.from_transport(transport, window_size=10) as sftp:
                create_remote_directory(sftp, remote_filepath)
                if are_files_similar(sftp, remote_filepath, local_filepath):
                    print(f"File '{local_filepath}' already exists on the remote server with the same content.")
                    return remote_filepath

                # Upload the file
                sftp.put(local_filepath, remote_filepath)
                print(f"File '{local_filepath}' uploaded to '{remote_filepath}' successfully.")
                return remote_filepath

    except Exception as e:
        print(f"Error uploading or checking file: {e}")
        return None


def test_upload():
    while True:
        # file = File.objects.filter().latest('id')
        try:
            # custom_log(f"start ssh upload for file: {file.file.name} to server.")
            custom_log(f"start ssh upload for file: 512MB.zip to server.")

            # Example usage
            local_filepath = '/var/www/512MB.zip'
            # remote_filepath = f"{DOWNLOAD_FOLDER}/{file.file_type}/{file.unique_code}"
            remote_filepath = f"{DOWNLOAD_FOLDER}/512MB.zip"
            ssh_host = 'u379344.your-storagebox.de'
            ssh_port = 22
            ssh_username = 'u379344'
            ssh_password = 'LKZMfmz2xrtzUhXr'
            upload_file_to_remote(local_filepath, remote_filepath, ssh_host, ssh_port, ssh_username, ssh_password)

            # return custom_log(f"{file.file.name} uploaded successfully to SSH server.")
            return custom_log(f"512MB.zip uploaded successfully to SSH server.")
        except Exception as e:
            # custom_log(f"problem happens during upload {file.file.name} to server. err: {e}")
            custom_log(f"problem happens during upload 512MB.zip to server. err: {e}")
            time.sleep(10)
