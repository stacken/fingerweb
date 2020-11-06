from django import forms
from django.core.mail import send_mail
from django.contrib.auth import forms as ca_forms
from django.forms import ValidationError
import json
import re
from .models import User

class UploadFileForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        try:
            return json.load(self.cleaned_data['file'])
        except:
            raise ValidationError("Must be proper json", code='badjson')

class MailMembersForm(forms.Form):
    subject = forms.CharField(label='Subject')
    message = forms.CharField(label='Message', widget=forms.Textarea)
    extra_to = forms.CharField(label='Extra To', required=False)
    recipients = forms.CharField(label='Recipients', required=False)

    def get_members(self):
        all_users = User.objects.all()

        # Retrieving all users that are members
        members = [user for user in all_users if user.is_member()]

        return members



class PasswordResetForm(ca_forms.PasswordResetForm):
    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        Override the default implementation to:
        1) Don't require a user to have an old password to use the password reset.
        2) Allow username@stacken.kth.se as well as (external) email address.
        """
        print("In override get_users, search for", email)
        match = re.match(r'^([a-z0-9_-]+)@stacken\.kth\.se$', email)
        if match:
            username = match.group(1)
            print("Club user name", username)
            active_users = User.objects.filter(username__iexact=username, is_active=True)
        else:
            print("Externam email", email)
            active_users = User.objects.filter(email__iexact=email, is_active=True)
        print("Found users:", active_users)
        return active_users
