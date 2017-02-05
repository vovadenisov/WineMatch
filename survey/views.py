import json
import requests

from django.db import IntegrityError
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.shortcuts import render_to_response
from django.core.mail import send_mail

import survey.sphinx as sphinx
from users.models import UserModel
from feedback.models import Feedback
from survey.models import Survey, Question, Wine, Country, Answer, Favorites


MAX_TRIES_COUNT = 3


def send_error_mail(message):
    admins_email = [email[1] for email in settings.ADMINS]
    try:
        send_mail('Redirect to main', message, settings.SERVER_EMAIL, admins_email, fail_silently=False)
    except Exception:
        pass


#def search_result(request):
#    return render_to_response(template_name="search_result.html", context={"request":request})


def main(request):
    return render_to_response(template_name="/index.html", context={"request":request})


#def search(request):
#    q = request.GET.get('query')
#    if q:
#        wine_ids = sphinx.search(q)
#        wines = {w.id: w for w in Wine.objects.filter(id__in=wine_ids)}
#        wines = [wines.get(id_) for id_ in wine_ids]
#    else:
#        wines = []
#    return render_to_response(template_name="search_result.html", context={'wines': wines, "request": request})


#def wine(request, wine_id):
#   try:
#       wines = [
#           Wine.objects.get(id=wine_id)
#       ]
#   except Wine.DoesNotExist:
#       wines = []
#   return render_to_response(template_name="result.html", context={'wines': wines, 'one_wine_page': True})


#def mobile_filtration(request):
#    countries = [c.name for c in Country.objects.all()]
#    return render_to_response(template_name="filtration.html", context={ "countries": countries,})


#def filtration(request):
#    categories = {}
#    #country_list = request.GET.getlist('country')
#    country = request.GET.get('country')
#    if country:
#        categories.update({'country__name': country})
#    for category in ('color', 'type'):
#        category_list = request.GET.getlist(category)
#        if category_list: categories.update({category + '__in': category_list})
#    for category in ('year__lt', 'year__gt', 'price__lt', 'price__gt'):
#        c = request.GET.get(category)
#        if c: categories.update({category: int(c)})
#    #sort = request.GET.get('sort')
#    #if sort: categories.update({'wine_to_sort__name': sort})
#    wines = Wine.objects.select_related("country").filter(**categories)[:50]
#    return render_to_response("filter_results.html", context={ "wines": wines})

def add_fav_to_wines(user, wines):
    wine_ids = [w.id for w in wines]
    wines = {w.id: w for w in wines}
    for f in Favorites.objects.filter(user=user).filter(wine_id__in=wine_ids):
        wines[f.wine_id].is_in_fav = True
    return list(wines.values())


def _get_answers(node, json_answers):
    answers = {
        a.api_answer_id: a.image 
        for a in Answer.objects.filter(api_node=node).filter(
            api_answer_id__in=[
                a['id'] for a in json_answers
            ]
        )
    }
    for a in json_answers:
        if answers.get(a['id']):
            a['image'] = answers.get(a['id'])
    return json_answers


def _render_question(q, answers, current_survey, context):
    context.update({
        "image": q.img,
        "text": q.get_question(),
        "answers": _get_answers(q.node, answers),#q.get_answers(),
        "survey": current_survey
    })
    answers_len = len(context["answers"])
    if answers_len < 5 and answers_len >= 2:
        return render_to_response(template_name="redesign/question{}answers.html".format(answers_len), context=context)
    else:
        return render_to_response(template_name="redesign/question_many_answers.html", context=context)


def _render_answers(user, wines_response, context):
    wines_list = wines_response["wines"]
    wines = []
    for wine in wines_list:
        try:
            w = Wine.objects.get(title=wine['title'])
            try:
                user.recommended_set.create(wine=w)
            except IntegrityError:
                pass
            wines.append(w)
        except Wine.DoesNotExist:
            pass #its ok to loose some wine
    wines = add_fav_to_wines(user, wines)
    context.update({"wines": wines})
    return render_to_response(template_name="redesign/match.html", context=context)


def survey(request):
#    if request.user.is_authenticated():
#        feedback = Feedback.objects.get_last_review(request.user.id) 
#        if feedback: return HttpResponseRedirect("/feedback")
        
    answer_pk = request.GET.get("answer")
    if not answer_pk:
        survey_context = {}
        if request.user.is_authenticated():
            survey_context.update({"user": request.user})
        current_survey = Survey.objects.create(**survey_context)
    else:
        if request.GET.get("survey"):
            current_survey = Survey.objects.get(pk=request.GET.get("survey"))
        else:
            send_error_mail("survey is missed in GET params")
            return HttpResponseRedirect("/")
    params = {
        "user_id": current_survey.pk,
    }
    if answer_pk:
        params.update({"answer_id": answer_pk})
    tries_count = 0
    while tries_count < 4:
        match_response = requests.get('/'.join((settings.MATCH_URL,"next")), params=params)
    
        if not match_response.status_code == 200:
            send_error_mail("next resonse return not 200 \n returned {}".format(match_response.text))
            return HttpResponseRedirect("/")
        match_response = json.loads(match_response.text)
        if match_response.get('question').get('node'): break
        tries_count = tries_count + 1

    context = {
            "request": request
    }
    question = match_response.get("question")
    is_end = match_response.get("is_end")
    #tries_count = 0
    try:
        q = Question.objects.get(node=question.get('node'))
    except Question.DoesNotExist:
        send_error_mail("returned question is not find node: {}".format(question))
        raise ValueError(question)
        return HttpResponseRedirect("/")

    #while tries_count < MAX_TRIES_COUNT:
    #    if is_end: break
    #    node = question["node"]
    #    try:
    #        q = Question.objects.get(node=node)
    #        break
    #    except Question.DoesNotExist:
     #       tries_count += 1

    if not is_end:
        return _render_question(q, question['answers'], current_survey, context)
    else:
        match_response = requests.get('/'.join((settings.MATCH_URL,"wine_list", str(survey.pk))))
        if not match_response.status_code == 200:    
            send_error_mail("next resonse return not 200 \n returned {}".format(match_response.text))
            return HttpResponseRedirect("/")
        match_response = json.loads(match_response.text)
        return _render_answers(request.user, match_response, context)


def _wine_description(wine):
    return {
        "title": wine.get_name(),
        "price": wine.price,
        'food': wine.food,
        "year": wine.year,
        "description": wine.description,
        "color": wine.color,
        "sweetness": wine.type,
        'country': wine.get_country(),
        'image': wine.img,
        'style': wine.stylistic
    }


#def survey_yesno(request):
#    return render_to_response(template_name="yesno.html", context={"request":request})


#def info(request):
#    return render_to_response(template_name="about_us.html", context={"request":request})


#def result(request):
#    return render_to_response(template_name="result.html", context={"request":request})


def favorite(request):
    def _add_is_in_fav(wine):
        wine.is_in_fav = True
        return wine

    if request.user.is_authenticated():
        user = UserModel.objects.get(username=request.user)
        favorites = user.get_favorits()
        wines = [ _add_is_in_fav(w.wine) for w in favorites]
        context = {
            "request": request,
            "wines": wines
        }
        return render_to_response(template_name="redesign/favorite.html", context=context)
    else:
        return HttpResponseForbidden()


def toggle_favorite(request):
    if not request.user.is_authenticated() or not request.POST.get('wine_id'):
        return HttpResponseForbidden()
    try:
        wine = Wine.objects.get(request.POST.get('wine_id'))
    except Wine.DoesNotExist:
        return HttpResponseForbidden()

    try:
        fav = Favorites.objects.get(user=user, wine=wine)
        fav.delete()
    except Favorites.DoesNotExist:
        Favorites.objects.create(user=user, wine=wine)
    return HttpResponse()

#def feedback(request):
#    if not request.user.is_authenticated():
#        return HttpResponseForbidden()
#    feed_back = Feedback.objects.get_last_review(request.user.id)
#    if not feed_back:
#        return HttpResponseRedirect("/")
#    return render_to_response(template_name="feedbackform.html", context={"wine": feed_back.wine, "request": request})


#def thnx_for_feedback(request):
#    return render_to_response(
#        template_name="thx_for_feedback.html", context={
#            'declined_flag': request.GET.get('declined'),
#            "request": request
#        }
#    )

def recommended(request):
    if request.user.is_authenticated():
        user = UserModel.objects.get(username=request.user)
        recommended = user.recommended_set.all()
        wines = [ w.wine for w in recommended ]
        context = {
            "request": request,
            "wines": add_fav_to_wines(request.user, wines)
        }
        return render_to_response(template_name="redesign/recommend.html", context=context)
    else:
        return HttpResponseForbidden()

