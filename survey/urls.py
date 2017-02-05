from django.conf.urls import url
from survey.views import *

urlpatterns = [
    url(r'^$', main, name="main"),
    url(r'^find/$', survey, name="survey_next"),
    #url(r'^yes_no/$', survey_yesno, name="survey_next_yesno"),
    #Surl(r'^info/$', info, name="info"),
    #url(r'^result/$', result, name="result"),
    url(r'^favorite/$', favorite, name="favorite"),
    url(r'^favorite/ajax/toggle/$', toggle_favorite, name="toggle_favorite"),
    url(r'^recommended/$', recommended, name='recommended'),
    #url(r'^feedback/$', feedback, name="feedback"),
    #url(r'^thnx/$', thnx_for_feedback, name="thnx"),
    #url(r'^search/$', search, name='search'),
    #url(r'^filtration/$', filtration, name='filtration'),
    #url(r'^filters/$', mobile_filtration, name='filters'),
    #url(r'^wine/(?P<wine_id>\d+)', wine, name='wine'),
    #url(r'^search_result/', search_result, name='search_result')
]
