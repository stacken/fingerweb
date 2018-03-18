from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Service

@login_required
def service(request, name):
    service = get_object_or_404(Service, name=name)
    action = request.POST.get('action')
    show_secret = action in ('generate', 'show')
    if action == 'generate':
        service.generate_password(request.user)

    account = service.account_for(request.user)
    return render(request, 'services/service.html', {
        'service': service,
        'has_account': account and True,
        'secret': show_secret and account and account.secret,
    })
