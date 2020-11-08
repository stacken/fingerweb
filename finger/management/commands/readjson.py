from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from optparse import make_option
from finger.models import Member
import json


class Command(BaseCommand):
    help = "Find and read user info from finger.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file",
            default="/afs/stacken.kth.se/home/stacken/finger_txt/finger.json",
            help="Source file (location of finger.json)",
        )

    def handle(self, **options):
        with open(options.get("file")) as data:
            with transaction.atomic():
                Member.objects.update_data(json.load(data))
