from django.core.management import BaseCommand
import requests
import json


class Command(BaseCommand):
    def handle(self, *args, **options):

        base_url = 'https://g.api.mega.co.nz/'
        # login and get session id
        login_data = {'a': 'us', 'user': 'email', 'uh': 'hash'}
        login_response = requests.post(base_url + 'cs', data=json.dumps([login_data]))
        session_id = login_response.json()[0]['csid']
        # get upload url and completion handle
        upload_data = {'a': 'u', 's': 1024, 'msid': session_id}
        upload_response = requests.post(base_url + 'cs', data=json.dumps([upload_data]))
        upload_url = upload_response.json()[0]['p']
        completion_handle = upload_response.json()[0]['h']
        # encrypt and upload file data
        filename = 'myfile.txt'
        file_data = open(filename, 'rb').read()
        file_key = generate_file_key()  # generate a random 256-bit key
        file_data_encrypted = encrypt_file_data(file_data, file_key)  # encrypt file data with AES-CTR
        upload_file_response = requests.post(upload_url, data=file_data_encrypted)
        # link file node to destination folder node
        folder_handle = 'xxxxxxxxxxxxxxxx'  # the handle of the destination folder
        file_attributes = {'n': filename}
        file_attributes_encrypted = encrypt_file_attributes(file_attributes,
                                                            file_key)  # encrypt file attributes with AES-CBC
        link_data = {'a': 'p', 't': folder_handle, 'n': [
            {'h': completion_handle, 't': 0, 'a': file_attributes_encrypted, 'k': encrypt_file_key(file_key)}],
                     'i': session_id}
        link_response = requests.post(base_url + 'cs', data=json.dumps([link_data]))
