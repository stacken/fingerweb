from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Service

# Create your views here.
def service(request, name):
    service = get_object_or_404(Service, name=name)
    if request.POST.get('action') == 'generate':
        service.generate_password(request.user)
        return redirect(request.path + "?show-secret=t")
    else:
        account = service.account_for(request.user)
        show_secret = request.GET.get('show-secret')
        return render(request, 'services/service.html', {
            'service': service,
            'has_account': account and True,
            'secret': show_secret and account and account.secret,
        })
