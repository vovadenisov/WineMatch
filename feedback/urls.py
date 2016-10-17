from django.conf.urls import url
from feedback.views import answer_review, decline_review, select_wine4review

urlpatterns = [
    url(r'^ajax/answer/$', answer_review, name="answer_review"),
    url(r'^ajax/decline/$', decline_review, name="decline_review"),
    url(r'^ajax/selectwine/$', select_wine4review, name="select_wine4review"),
]
