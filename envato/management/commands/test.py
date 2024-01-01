from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import token_generator
from custom_logs.models import CustomLog




class Command(BaseCommand):
    def handle(self, *args, **options):

        for user in User.objects.filter():
            print(user.username)
        user = User.objects.get(username='admin')
        profile = user.user_profile
        print(profile)
