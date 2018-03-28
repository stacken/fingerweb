from django.conf import settings
from django.core.management.base import BaseCommand
from optparse import make_option
from finger.models import User
import json

class Command(BaseCommand):
    help = 'Find and read user info from finger.json'

    def add_arguments(self, parser):
        parser.add_argument('--file', dest='file',
                            default='/afs/stacken.kth.se/home/stacken/finger_txt/finger.json',
                            help='Source file (location of finger.json)')

    def handle(self, **options):
        with open(options.get('file')) as data:
            User.objects.update_data(json.load(data))
