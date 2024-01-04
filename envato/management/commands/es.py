import re

from django.core.management.base import BaseCommand

from envato.enva_def import envato_auth, envato_auth_all, envato_download_file, check_if_sign_in_is_needed, \
    get_envato_cookie
from envato.models import EnvatoAccount, EnvatoFile


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            envato_accounts = EnvatoAccount.objects.filter(is_account_active=True)
            if envato_accounts.count() != 0:
                envato_account = envato_accounts.latest('id')
            else:
                raise
            # check_if_sign_in_is_needed(envato_account)
            # get_envato_cookie(envato_account)
            envato_files = EnvatoFile.objects.filter(file='', in_progress=False, is_acceptable_file=True)
            for file in envato_files:
                file.in_progress = True
                file.save()
            envato_download_file(envato_files, envato_account)
        except Exception as e:
            print(str(e))