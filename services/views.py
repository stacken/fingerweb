from base64 import b64decode
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
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

def passwords(request, name):
    auth_user, auth_key = basic_auth(request)
    service = get_object_or_404(Service, name=name)
    if auth_user != name or not check_password(auth_key, service.password):
        return HttpResponseForbidden()

    query = service.serviceuser_set
    since = request.GET.get('since')
    if since:
        since = datetime.strptime(since, '%Y-%m-%dT%H:%M:%S%Z')
        query = query.filter(modified__gte=since)

    return JsonResponse(dict(
        query.values_list('user__username', 'secret')
    ))

def basic_auth(request):
    auth_data = request.META.get('HTTP_AUTHORIZATION')
    if not auth_data:
        return None, None
    auth_method, auth_data = auth_data.split(' ')
    if auth_method != 'Basic':
        return None, None
    auth_user, auth_key = str(b64decode(auth_data), 'ascii').split(':')
    return auth_user, auth_key
