from django.core.management import BaseCommand

from accounts.models import UserRequestHistory
from core.models import get_core_settings, File
from scrapers.models import MotionArrayAccount, EnvatoAccount


class Command(BaseCommand):
    def handle(self, *args, **options):
        # motion_array_accounts = MotionArrayAccount.objects.filter(is_account_active=True,
        #                                                           number_of_daily_usage__lte=get_core_settings().motion_array_account_total_daily_limit).order_by(
        #     'number_of_daily_usage').first()
        #
        # print(motion_array_accounts)
        #
        # envato_accounts = EnvatoAccount.objects.filter(is_account_active=True,
        #                                                number_of_daily_usage__lte=get_core_settings().envato_account_total_daily_limit).order_by(
        #     'number_of_daily_usage')
        # print(envato_accounts)

        File.objects.all().delete()
        UserRequestHistory.objects.all().delete()
