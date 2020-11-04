from django.contrib.auth import views  as ca_views
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render
from services.models import Service
from .forms import PasswordResetForm, UploadFileForm, MailMembersForm
from .models import User

@login_required
def index(request):
    return render(request, 'home.html', {
        'services': Service.objects.all()
    })

@login_required
def upload_json(request):
    if not (request.user.is_staff and request.user.is_superuser):
        return HttpResponseNotAllowed()
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

@login_required
def mail_members(request):
    if not (request.user.is_staff and request.user.is_superuser):
        return HttpResponseNotAllowed()  

    if request.method == 'POST':
        form = MailMembersForm(request.POST)
        m = form.get_members()

        if not request.POST.get("do_it", "") == "true":
            context = {
                'members' : m,
                'form' : form,
                'test' : True,
            }          
        else:
            context = {
                'members' : m,
                'form' : form,
                'test' : False,
            }
        
        return render(request, 'mail_members_test.html', context)
    else:
        form = MailMembersForm()

    return render(request, 'mail_members.html', {
        'form': form,
        
    })

class PasswordResetView(ca_views.PasswordResetView):
    """Override djago.contrib.auth to use custom Form object."""
    form_class = PasswordResetForm
