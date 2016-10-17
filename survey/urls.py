from django.conf.urls import url
from survey.views import main, survey, survey_yesno, info, result, favorite

urlpatterns = [
    url(r'^$', main, name="main"),
    url(r'^find/$', survey, name="survey_next"),
    url(r'^yes_no/$', survey_yesno, name="survey_next_yesno"),
    url(r'^info/$', info, name="info"),
    url(r'^result/$', result, name="result"),
    url(r'^favorite/$', favorite, name="favorite"),
]