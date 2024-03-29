import os
import time
from django.core.management import BaseCommand

from accounts.models import UserMultiToken


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_multi_tokens = UserMultiToken.objects.all()
        for user_multi_token in user_multi_tokens:
            user_multi_token.disabled = False
            user_multi_token.save()
