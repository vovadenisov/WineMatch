from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model, login


def authenticate_middleware(get_response):

    def all_authenticate(request):
        if not request.user.is_authenticated:
            with transaction.atomic():
                users = get_user_model().objects.all()
                if users:
                    last_user_pk = users.last().pk
                else:
                    last_user_pk = 0
                user = get_user_model().objects.create(username=str(last_user_pk + 1))
            login(request, user)
        response = get_response(request)
        return response
    return all_authenticate
