from django.conf.urls import url

from users.views import vk_user_authenticate, fb_user_auth, logout_view

urlpatterns = [
    url(r'^auth_user/$', vk_user_authenticate, name="vk_auth"),
    url(r'^fb_auth_user/$', fb_user_auth, name="fb_auth"),
    url(r'^logout/$', logout_view, name="logout")
]