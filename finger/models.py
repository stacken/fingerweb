from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as AuthUserManager
from django.db import models
import re
from dateutil import parser
from datetime import datetime

class UserManager(AuthUserManager):

    def is_valid_user(self, user):
        username = user.get('användarnamn')
        return username and re.match('^[a-z]+$', username) and username != 'stacken'

    def list_to_str(self, the_list):
        return ", ".join(filter(None, the_list))

    def update_data(self, data):
        """
        Take an iterable of user data (the result of parsing finger.json),
        and create and/or update users accordingly.
        """

        for user in data:
            if self.is_valid_user(user):
                fields = {}

                # I see no point to keep _both_ values in separate fields. No script
                # uses them, they are only for human consumption. Make the list unique.
                fields['phone'] = self.list_to_str(
                    list(set([user.get('arbtelefon'), user.get('hemtelefon')]))
                )

                # Various information in the commens field, this contains possible
                # useful infomation for the future. But it's intended for human
                # consumption and the information is not that usable these days.
                fields['comments'] = self.list_to_str(
                    [
                        user.get('avdelning'),
                        user.get('distrubution'),
                        user.get('organisation'),
                        user.get('status'),
                        user.get('syssel'),
                        user.get('comment'),
                        "Medlemmen är utesluten" if user.get('Utesluten') else ""
                    ]
                )

                # Unless we have noted the address as incorrect, add the information
                # to the address field.
                if not user.get('Fel_adress'):
                    fields['address'] = self.list_to_str(
                        [
                            "c/o " + user.get('c/o') if user.get('c/o') else "",
                            user.get('gatuadress'),
                            user.get('postadress'),
                            user.get('land')
                        ]
                    )

                # Because the user can choose to pay only for half the year we need to
                # verify THS members twice a year. In the old system we only noted what
                # year we checked the membership status.
                if datetime.now().month <= 7:
                    fields['ths_claimed_vt'] = user.get('THS-studerande')
                else:
                    fields['ths_claimed_ht'] = user.get('THS-studerande')

                # Various simple fields that do not need that much comments...
                fields['title'] = user.get('titel')
                fields['first_name'] = user.get('förnamn')
                fields['last_name'] = user.get('efternamn')
                fields['payed_year'] = user.get('betalt')
                fields['has_key'] = user.get('Hallnyckel', False)
                fields['support_member'] = user.get('stödmedlem', False)
                fields['honorary_member'] = user.get('Hedersmedlem', False)
                fields['keycard_number'] = user.get('kortnr')
                fields['date_joined'] = parse_date(user.get('inträdesdatum', '1970-01-01'))

                # These fields are mainly here to make our verifications easier. Both with new
                # members but also when we talk with THS. The field ths_name is intended to be
                # used insted of first_ and last_name when we talk with THS. This can be useful
                # if the name in Stackens systems does not match what THS has on file.
                fields['ths_name'] = user.get('THS-namn')
                fields['kth_account'] = user.get('KTH-konto')

                # If the user has a kth.se-email address, assume the user part is the KTH account name
                if user.get('mailadress') and "@" in user.get('mailadress') and not user.get('KTH-konto'):
                    email_fields = user.get('mailadress').split("@")
                    if email_fields[1] == "kth.se":
                        fields['kth_account'] = email_fields[0]

                # For users that do not have an email address try to construct one with the
                # information we have on file.
                if user.get('mailadress'):
                    fields['email'] = user.get('mailadress')
                else:
                    kthname = user.get('KTH-konto')
                    username = user.get('användarnamn')
                    if kthname:
                        fields['email'] = kthname + '@kth.se'
                    else:
                        fields['email'] = username + '@stacken.kth.se'

                # For users that have left the club. Set a parted date and disable the user.
                if user.get('utträdesdatum'):
                    fields['date_parted'] = parse_date(user.get('utträdesdatum'))
                    fields['is_active'] = False
                else:
                    fields['date_parted'] = None
                
                # Disable users that have have parted
                if user.get('Utesluten') or user.get('Slutat'):
                    fields['is_active'] = False

                user, created = self.update_or_create(username=user.get('användarnamn'),
                                                      defaults=fields)

def parse_date(datestr):
    if datestr:
        return parser.parse("%s 12:00:00 CET" % datestr)
    else:
        return None


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
    honorary_member = models.BooleanField(default=False, verbose_name="Honorary Member", help_text="If the member is a honorary member.")
    support_member = models.BooleanField(default=False, verbose_name="Support Member", help_text="The memeber is an support member, the member has no voting rights.")
    keycard_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Keycard Number", help_text="The number of KTH's keycard, used by us to grant members access to the clubroom.")
    kth_account = models.CharField(null=True, blank=True, max_length=255, verbose_name="KTH account", help_text="The KTH accound name, useful when validating THS membership status.")
    ths_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="THS Name", help_text="If the member is known by some other name in THS systems, this will override the name when we validates THS membership status.")
    title = models.CharField(null=True, blank=True, max_length=255, verbose_name="Title", help_text="An optional title to the member.")
    date_parted = models.DateTimeField(null=True, blank=True, verbose_name="Date parted", help_text="The date of when a member left the club.")

    objects = UserManager()

    def is_member(self):
        """
        Return status if the user is considered an active member. If the user as
        a parted date, is not active or has not payed or verified THS membership
        this year, consider the user not a member.
        """

        if self.has_parted():
            return False

        this_year = datetime.now().year
        if self.last_member(format=2) >= this_year:
            return True
        else:
            return False
    is_member.boolean = True

    def is_account_disabled(self):
        """
        Like is_member, but give the user one extra year before the account is
        disabled. This is nice and it makes the transision periodes like new
        year easier to manage.
        """

        if self.has_parted():
            return False

        this_year = datetime.now().year
        if self.last_member(format=2) < this_year - 1:
            return True
        else:
            return False

    def is_account_delete(self):
        """
        Like is_account_disabled, but 5 years instead of 1. This is used to figure
        out what accounts we should remove.
        """
        if self.has_parted():
            return False

        this_year = datetime.now().year
        if self.last_member(format=2) < this_year - 5:
            return True
        else:
            return False

    def ths_claimed(self):
        """
        The user is a THS member
        """
        t = datetime.now()
        if t.month <= 7:
            return self.ths_claimed_vt == t.year
        else:
            return self.ths_claimed_ht == t.year
    ths_claimed.boolean = True

    def ths_verified(self):
        """
        The user is a THS verified member
        """
        t = datetime.now()
        if t.month <= 7:
            return self.ths_verified_vt == t.year
        else:
            return self.ths_verified_ht == t.year
    ths_verified.boolean = True

    def has_parted(self):
        """
        Checks if the user has parted or not from the club.
        TODO: Also check that the date is in the past
        """
        return self.date_parted or not self.is_active


    def last_member(self, format=1):
        """
        Calculate last time this member was a member. Return a nice year from the
        middle ages if the information is missing in the database. Honorary members
        do not need to pay a member fee so they are considered members until they
        leave.
        """
        if self.honorary_member:
            if format == 2:
                return datetime.now().year
            else:
                return str(datetime.now().year)

        bucket = [1337]
        bucket.append(self.payed_year)
        bucket.append(self.ths_claimed_ht)
        bucket.append(self.ths_claimed_vt)

        r = max([b for b in bucket if b])
        if format == 2:
            return r
        return str(r)
