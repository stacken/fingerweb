from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as AuthUserManager
from django.db import models
import re
from dateutil import parser

class UserManager(AuthUserManager):
    def update_data(self, data):
        """
        Take an iterable of user data (the result of parsing finger.json),
        and create and/or update users accordingly.
        """
        for entry in data:
            username = entry.get('användarnamn')
            if username and re.match('^[a-z]+$', username) and username != 'stacken':

                phone_list = [entry.get('arbtelefon'),
                              entry.get('hemtelefon')]

                comments_list = [entry.get('avdelning'),
                                 entry.get('distrubution'),
                                 entry.get('organisation'),
                                 entry.get('status'),
                                 entry.get('syssel'),
                                 entry.get('comment')]
                if entry.get('Utesluten'):
                    comments_list = ["Utesluten"] + comments_list

                if not entry.get('Fel_adress'):
                    address_list = [entry.get('gatuadress'),
                                    entry.get('postadress'),
                                    entry.get('land')]
                    if entry.get('c/o'):
                        address_list = ["c/o " + entry.get('c/o')] + address_list
                else:
                    address_list = []

                fields = {
                    'title': entry.get('titel'),
                    'first_name': entry.get('förnamn'),
                    'last_name': entry.get('efternamn'),
                    'email': entry.get('mailadress'),
                    'payed_year': entry.get('betalt'),
                    'ths_claimed_vt': entry.get('THS-studerande'),
                    'ths_claimed_ht': entry.get('THS-studerande'),
                    'phone': ", ".join(filter(None, phone_list)),
                    'comments': "\n".join(filter(None, comments_list)),
                    'address': "\n".join(filter(None, address_list)),
                    'ths_name': entry.get('THS-namn'),
                    'kth_account': entry.get('KTH-konto'),
                    'has_key': entry.get('Hallnyckel', False),
                    'support_member': entry.get('stödmedlem', False),
                    'honourable_member': entry.get('Hedersmedlem', False),
                    'keycard_number': entry.get('kortnr'),
                    'date_joined': parser.parse(entry.get('inträdesdatum', '1970-01-01')),
                }
                if not fields.get('email'):
                    kthname = entry.get('KTH-konto')
                    if kthname:
                        fields['email'] = kthname + '@kth.se'
                    else:
                        fields['email'] = username + '@stacken.kth.se'

                if entry.get('utträdesdatum'):
                    fields['date_parted'] = parser.parse(entry.get('utträdesdatum'))
                    fields['is_active'] = False
                else:
                    fields['date_parted'] = None

                if entry.get('Utesluten') or entry.get('Slutat'):
                    fields['is_active'] = False

                user, created = self.update_or_create(username=username,
                                                      defaults=fields)

class User(AbstractUser):
    payed_year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Payed Year", help_text="The year the member has valid payed membership to.")
    ths_verified_vt = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="THS Verified Member VT", help_text="The member is verified to be a THS member for the fist half of the specified year.")
    ths_verified_ht = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="THS Verified Member HT", help_text="The member is verified to be a THS member for the second half of the specified year.")
    ths_claimed_vt = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="THS Claimed Member VT", help_text="The member has claimed to be a THS member for the fist half of the specified year.")
    ths_claimed_ht = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="THS Claimed Member HT", help_text="The member has claimed to be a THS member for the second half of the specified year.")
    phone = models.CharField(null=True, blank=True, max_length=255, verbose_name="Phone", help_text="One or several phone numbers to the member.")
    comments = models.TextField(null=True, blank=True, verbose_name="Comments", help_text="One or more comments about the member.")
    address = models.TextField(null=True, blank=True, verbose_name="Address", help_text="The members address.")
    has_key = models.BooleanField(default=False, verbose_name="Has a Key", help_text="If the member has a key to the computer hall.")
    honourable_member = models.BooleanField(default=False, verbose_name="Honourable Member", help_text="If the member is a Honourable member.")
    support_member = models.BooleanField(default=False, verbose_name="Support Member", help_text="The memeber is an support member, the member has no voting rights.")
    keycard_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Keycard Number", help_text="The number of KTH's keycard, used by us to grant members access to the clubroom.")
    kth_account = models.CharField(null=True, blank=True, max_length=255, verbose_name="KTH account", help_text="The KTH accound name, useful when validating THS membership status.")
    ths_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="THS Name", help_text="If the member is known by some other name in THS systems, this will override the name when we validates THS membership status.")
    title = models.CharField(null=True, blank=True, max_length=255, verbose_name="Title", help_text="An optional title to the member.")
    date_parted = models.DateTimeField(null=True, blank=True, verbose_name="Date parted", help_text="The date of when a member left the club.")

    objects = UserManager()
