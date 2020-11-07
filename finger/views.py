import sys

from django.contrib.auth import views as ca_views
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mass_mail
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from finger.decorators import staff_or_superuser_required
from services.models import Service

from .forms import MailMembersForm, PasswordResetForm, UploadFileForm
from .models import User


@login_required
def index(request):
    return render(request, 'home.html', {
        'services': Service.objects.all()
    })

@staff_or_superuser_required
def upload_json(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                User.objects.update_data(form.cleaned_data['file'])
            return HttpResponseRedirect('/admin/finger/user/')
    else:
        form = UploadFileForm()
    return render(request, 'upload_json.html', {
        'form': form,
    })

@staff_or_superuser_required
def mail_members(request):
    if request.method == 'POST':
        form = MailMembersForm(request.POST)
    else:
        form = MailMembersForm()

    if form.is_valid():
        members = form.get_members()

        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        sender = request.user.username + '@stacken.kth.se'

        recipients = form.cleaned_data['recipients']
        if recipients:
            recipients = [("", [recipient]) for recipient in recipients.split(',')]
        else:
            recipients = [(f"{member.first_name} {member.last_name}", [member.email, f"{member.username}@stacken.kth.se" ]) for member in members]


        extra_to = form.cleaned_data['extra_to']
        if not extra_to:
            extra_to = "styrelsen@stacken.kth.se"
        recipients.append(('', [extra_to]))

        context = {
                'recipients' : recipients,
                'form' : form,
                'test' : True,
                'exception' : None,
        }   

        if request.POST.get("do_it", "") == "true":
            context['test'] = False
            messages = [(subject, message, sender, email) for (_, email) in recipients]
            try:
                send_mass_mail(messages, fail_silently=False)
            except:
                context['exception'] = sys.exc_info()

        
        return render(request, 'mail_members_test.html', context)

    return render(request, 'mail_members.html', {
        'form': form,
    })

class PasswordResetView(ca_views.PasswordResetView):
    """Override djago.contrib.auth to use custom Form object."""
    form_class = PasswordResetForm
