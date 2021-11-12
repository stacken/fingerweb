from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from optparse import make_option
from finger.models import Member
from finger.models import User


class Command(BaseCommand):
    help = "Update the database, execute with cron"

    def handle(self, **options):

        print("Processing members")
        with transaction.atomic():
            for member in Member.objects.all():
                if member.is_inactive():
                    users = User.objects.filter(member=member.id, is_active=True)
                    for user in users:
                        print(f"Disable {user} (member {member})")
                        user.is_active = False
                        user.save()

        print("Processing users")
        with transaction.atomic():
            for user in User.objects.filter(is_active=False):
                if not user.member.is_inactive():
                    print(f"Enable {user} (member {user.member})")
                    user.is_active = True
                    user.save()
