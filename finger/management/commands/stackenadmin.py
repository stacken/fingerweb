from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from optparse import make_option
from finger.models import User
from os import environ


class Command(BaseCommand):
    help = "Find and read user info from finger.json"

    def handle(self, **options):
        password = environ.get("DJANGOADMIN_PASSWORD")
        if not password:
            print("No password given.  No admin created")
            return
        User.objects.filter(username="admin").delete()
        User.objects.create_superuser("admin", "staff@stacken.kth.se", password)
        print("Created/updated admin accout")
