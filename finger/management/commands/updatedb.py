from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from optparse import make_option
from finger.models import Member
import json


class Command(BaseCommand):
    help = "Update the database, execute with cron"

    def handle(self, **options):
        with transaction.atomic():
            Member.objects.inspect_data()
