from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from services.models import Service

@login_required
def index(request):
    return render(request, 'home.html', {
        'services': Service.objects.all()
    })
