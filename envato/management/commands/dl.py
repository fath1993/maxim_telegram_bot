import time

from django.core.management import BaseCommand
import http.client
import aria2p


class Command(BaseCommand):
    def handle(self, *args, **options):
        download_test()


def download_test():
    url = 'https://u379344.your-storagebox.de/2231/envato/UBA7MRY'
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )
    # Specify custom options as a dictionary
    custom_options = {
        'user-agent': 'Chrome/115.0.0.0',
        'out': f'/var/www/maxim_telegram_bot_dev/envato/management/commands',
    }
    if str(url).find('storagebox.de') != -1:
        webdav_host = "u379344.your-storagebox.de"
        webdav_port = 443
        webdav_path = str(url).split('storagebox.de')[-1]
        webdav_username = "u379344"
        webdav_password = "LKZMfmz2xrtzUhXr"

        # Connect to the WebDAV server
        connection = http.client.HTTPConnection(webdav_host, webdav_port)

        # Specify the URL with username and password
        url = f"https://{webdav_username}:{webdav_password}@{webdav_host}:{webdav_port}{webdav_path}"
    else:
        pass
    download = aria2.add_uris([f"{url}"], options=custom_options)

    while not download.is_complete:
        download.update()
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
        time.sleep(1)