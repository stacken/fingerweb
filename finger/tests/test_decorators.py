import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from finger.models import User
from finger.decorators import staff_or_superuser_required


@pytest.mark.parametrize(
    "is_staff,is_superuser,expected_response_code",
    (
        (False, False, 403),
        (True, False, 403),
        (False, True, 403),
        (True, True, 200),
    )
)
def test_staff_or_superuser__only_allows_staff_superusers(
        is_staff, is_superuser, expected_response_code
):
    @staff_or_superuser_required
    def some_test_view(_request):
        return HttpResponse("All is ok")

    user = User(is_staff=is_staff, is_superuser=is_superuser)

    request = RequestFactory().get('/some-test-view')
    request.user = user

    response = some_test_view(request)

    assert response.status_code == expected_response_code
