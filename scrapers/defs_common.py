import os
import re
import threading
import aria2p
import time
import subprocess
import paramiko
from custom_logs.models import custom_log
from maxim_telegram_bot.settings import DOWNLOAD_FOLDER


def check_chrome_connection_status(driver_object):
    for entry in driver_object.get_log('performance'):
        if str(entry['message']).find('"errorText":"net::ERR_TIMED_OUT"') != -1:
            errorText = "net::ERR_NO_SUPPORTED_PROXIES"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_NO_SUPPORTED_PROXIES"') != -1:
            errorText = "net::ERR_NO_SUPPORTED_PROXIES"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_INTERNET_DISCONNECTED"') != -1:
            errorText = "net::ERR_INTERNET_DISCONNECTED"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_CONNECTION_TIMED_OUT"') != -1:
            errorText = "net::ERR_CONNECTION_TIMED_OUT"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_CONNECTION_RESET"') != -1:
            errorText = "net::ERR_CONNECTION_RESET"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_CONNECTION_REFUSED"') != -1:
            errorText = "net::ERR_CONNECTION_REFUSED"
            custom_log(errorText, f"scrapers")
            return ConnectionError


def download_file_with_aria2_download_manager(file, file_name: str, url: str):
    if file.file_type == 'envato':
        folder_name = 'envato'
    elif file.file_type == 'motion_array':
        folder_name = 'motion_array'
    else:
        return False

    file.download_percentage = 0
    file.save()
    time.sleep(0.1)

    # Direct aria2c
    if str(url).find('storagebox.de') != -1:
        try:
            webdav_host = "u379344.your-storagebox.de"
            webdav_port = 443
            webdav_path = str(url).split('storagebox.de')[-1]
            webdav_username = "u379344"
            webdav_password = "LKZMfmz2xrtzUhXr"

            # Specify the URL with username and password
            url = f"https://{webdav_username}:{webdav_password}@{webdav_host}:{webdav_port}{webdav_path}"

            # Command to download with aria2c
            command = [
                f'aria2c',
                f'--user-agent=Chrome/124.0.0.0',
                f'--out={file_name}',
                f'--dir=/var/www/maxim_telegram_bot/media/{folder_name}/files/',
                f'--continue=true',
                f'{url}'
            ]

            # Start the aria2c command with stdout redirected to a pipe
            process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)

            # Regular expression pattern to match the completion percentage
            pattern = r'\((\d+)%\)'

            # Read and process the output line by line in real-time
            for line in iter(process.stdout.readline, ''):
                match = re.search(pattern, line)
                if match:
                    latest_completion_percentage = match.group(1)
                    if latest_completion_percentage is not None:
                        file.download_percentage = int(str(latest_completion_percentage).replace('%', ''))
                        file.save()
                time.sleep(0.5)

            # Wait for the aria2c command to finish
            process.wait()

            custom_log(
                f'download_file_with_aria2_download_manager. result: download file: {file.unique_code} has been finished successfully',
                f"scrapers")
            file.download_percentage = 100
            file.is_acceptable_file = True
            file.in_progress = False
            file.file.name = f'/{folder_name}/files/{file_name}'
            file.save()
            return True
        except Exception as e:
            custom_log(f'download_file_with_aria2_download_manager. try/except:> err: {str(e)}', f"scrapers")
            return False
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret="",
        )
    )
    # Specify custom options as a dictionary
    custom_options = {
        'user-agent': 'Chrome/124.0.0.0',
        'out': f'{file_name}',
        'dir': f'/var/www/maxim_telegram_bot/media/{folder_name}/files/',
        'max-concurrent-downloads': '8',
        'max-connection-per-server': '8',
        'continue': 'true',

    }

    download = aria2.add_uris([f"{url}"], options=custom_options)

    attempt = 0
    while not download.is_complete:
        download.update()
        time.sleep(1)
        custom_log(f'{download.status}', 'download_manager')
        try:
            if download.status == 'error':
                download.pause()
            speed = download.download_speed
            completed_length = download.completed_length
            total_length = download.total_length
            percentage = download.progress
            print(f"download: {download.status}")
            print(f"Download Speed: {speed}")
            print(f"Downloaded: {completed_length}")
            print(f"Remaining: {total_length}")
            print(f"Completion Percentage: {percentage}%")
            print("------------")
            attempt = 0
            if int(percentage) != 100:
                file.download_percentage = int(percentage)
                file.save()
                time.sleep(1)
        except Exception as e:
            attempt += 1
            custom_log(f'download_file_with_aria2_download_manager. try/except:> err: {str(e)}', f"scrapers")
            if attempt == 10:
                file.download_percentage = 0
                file.is_acceptable_file = True
                file.in_progress = False
                file.save()
                return False
            time.sleep(1)
    if download.is_complete:
        try:
            file.download_percentage = 100
            file.is_acceptable_file = True
            file.in_progress = False
            file.file.name = f'/{folder_name}/files/{file_name}'
            file.save()
            if str(url).find('storagebox.de') == -1:
                UploadManager(file).start()
            custom_log(f'download_file_with_aria2_download_manager. result: download file: {file.unique_code} has been finished successfully', f"scrapers")
            return True
        except Exception as e:
            custom_log(f'download_file_with_aria2_download_manager. try/except:> err: {str(e)}', f"scrapers")
            return False
    else:
        custom_log(f'download_file_with_aria2_download_manager. download problem', f"scrapers")
        return False



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

                sftp.put(local_filepath, remote_filepath)
                print(f"File '{local_filepath}' uploaded to '{remote_filepath}' successfully.")
                return remote_filepath

    except Exception as e:
        print(f"Error uploading or checking file: {e}")
        return None


class UploadManager(threading.Thread):
    def __init__(self, file):
        super().__init__()
        self.file = file
        if file.file_type == 'envato':
            self.folder_name = 'envato'
        elif file.file_type == 'motion_array':
            self.folder_name = 'motion_array'
        else:
            pass

    def run(self):
        number_of_try = 0
        while True:
            try:
                custom_log(f"start ssh upload for file: {self.file.file.name} to server.", f"scrapers")
                local_filepath = f'/var/www/maxim_telegram_bot/{self.file.file.url}'
                file_name, file_extension = os.path.splitext(self.file.file.url)
                remote_filepath = f"/{DOWNLOAD_FOLDER}/{self.folder_name}/{self.file.unique_code}{file_extension}"
                ssh_host = 'u379344.your-storagebox.de'
                ssh_port = 22
                ssh_username = 'u379344'
                ssh_password = 'LKZMfmz2xrtzUhXr'
                upload_file_to_remote(local_filepath, remote_filepath, ssh_host, ssh_port, ssh_username, ssh_password)
                self.file.file_storage_link = ssh_host + remote_filepath
                self.file.save()
                return custom_log(f"{self.file.file.name} uploaded successfully to SSH server.", f"scrapers")
            except Exception as e:
                custom_log(f"problem happens during upload {self.file.file.name} to server. err: {e}", f"scrapers")
                number_of_try += 1
                time.sleep(10)
            if number_of_try == 3:
                return custom_log(f"after 3 times reload, {self.file.file.name} didnt upload to server successfully.", f"scrapers")


