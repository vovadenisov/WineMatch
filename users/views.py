from django.contrib.auth import get_user_model, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

# Create your views here.
from users.models import UserModel


def vk_user_authenticate(request):
    vk_user_id = request.GET.get("mid")
    try:
        user = get_user_model().objects.get(vk_id=vk_user_id)
        login(request, user)
        # todo добавить сюда логику для схлопывания юзеров при авторизации
    except UserModel.DoesNotExist:
        user = get_user_model().objects.create(username=str(vk_user_id), vk_id=str(vk_user_id))
        login(request, user)
    return HttpResponse()


def fb_user_auth(request):
    return render_to_response(template_name="facebook_auth.html", context={})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

