from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as AuthUserManager
from django.db import models
import re

class UserManager(AuthUserManager):
    def update_data(self, data):
        """
        Take an iterable of user data (the result of parsing finger.json),
        and create and/or update users accordingly.
        """
        for entry in data:
            username = entry.get('användarnamn')
            if username and re.match('^[a-z]+$', username) and username != 'stacken':
                fields = {
                    'first_name': entry.get('förnamn'),
                    'last_name': entry.get('efternamn'),
                    'email': entry.get('mailadress'),
                }
                if not fields.get('email'):
                    kthname = entry.get('KTH-konto')
                    if kthname:
                        fields['email'] = kthname + '@kth.se'
                    else:
                        fields['email'] = username + '@stacken.kth.se'
                user, created = self.update_or_create(username=username,
                                                      defaults=fields)

class User(AbstractUser):
    payed_year = models.PositiveSmallIntegerField(null=True)
    ths_verified_vt = models.PositiveSmallIntegerField(null=True)
    ths_verified_ht = models.PositiveSmallIntegerField(null=True)
    ths_claimed_vt = models.PositiveSmallIntegerField(null=True)
    ths_claimed_ht = models.PositiveSmallIntegerField(null=True)

    objects = UserManager()
