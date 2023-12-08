from django.core.management.base import BaseCommand
from finger.models import User
from os import environ
from dateutil import parser


class Command(BaseCommand):
    help = "Find and read user info from finger.json"

    def handle(self, **options):
        password = environ.get("DJANGOADMIN_PASSWORD")
        if not password:
            print("No password given. No admin created/updated")
            return

        # Fix for developers, PR #28 fixed an bug where is_active and
        # data_joined was not set propperly. This code can be removed
        # in the future.
        if User.objects.filter(username="admin", is_active=None).exists():
            print("Admin user needs to be recreated")
            User.objects.filter(username="admin").delete()

        if User.objects.filter(username="admin").exists():
            print("Admin user already exists, update the existing user")
            User.objects.get(username="admin").set_password(password)
        else:
            print("Create admin accout")
            User.objects.create_superuser(
                "admin",
                "staff@stacken.kth.se",
                password,
                is_active=True,
                date_joined=parser.parse("1970-01-01 00:00:01 CET"),
            )
