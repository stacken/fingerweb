"""
A module to collect custom decorators that we use throughout fingerweb.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils.functional import wraps


def staff_or_superuser_required(view):
    """
    Require a logged in user that is both staff _and_ a superuser.

    Usage:

        from fingerweb.decorators import staff_or_superuser_required

        @staff_or_superuser_required
        def my_view(request): ...
    """

    @login_required
    @wraps(view)
    def inner(request, *args, **kwargs):
        if not (request.user.is_staff and request.user.is_superuser):
            return HttpResponseForbidden()

        return view(request, *args, **kwargs)

    return inner
