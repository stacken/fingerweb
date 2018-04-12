from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render
from services.models import Service
from .forms import UploadFileForm
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
