from django.conf.urls import url
from survey.views import *

urlpatterns = [
    url(r'^$', main, name="main"),
    url(r'^find/$', survey, name="survey_next"),
    url(r'^yes_no/$', survey_yesno, name="survey_next_yesno"),
    url(r'^info/$', info, name="info"),
    url(r'^result/$', result, name="result"),
    url(r'^favorite/$', favorite, name="favorite"),
    url(r'^feedback/$', feedback, name="feedback"),
    url(r'^thnx/$', thnx_for_feedback, name="thnx"),
    url(r'^search/$', search, name='search'),
    url(r'^filtration/$', filtration, name='filtration'),
    url(r'^mobile_filtration/$', mobile_filtration, name='mobile_filtration'),
    url(r'^wine/(?P<wine_id>\d+)', wine, name='wine'),
    url(r'^wine/(?P<wine_id>\d+)', wine, name='wine'),
    url(r'^search_result/', search_result, name='search_result')
]
