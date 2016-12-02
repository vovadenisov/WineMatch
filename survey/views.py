import json
import requests

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.shortcuts import render_to_response
from django.core.mail import send_mail

import survey.sphinx as sphinx
from users.models import UserModel
from feedback.models import Feedback
from survey.models import Survey, Question, Wine, Country


MAX_TRIES_COUNT = 3


def send_error_mail(message):
    admins_email = [email[1] for email in settings.ADMINS]
    try:
        send_mail('Redirect to main', message, settings.SERVER_EMAIL, admins_email, fail_silently=False)
    except Exception:
        pass


def search_result(request):
    return render_to_response(template_name="search_result.html", context={"request":request})


def main(request):
    return render_to_response(template_name="main.html", context={"request":request})


def search(request):
    q = request.GET.get('query')
    if q:
        wine_ids = sphinx.search(q)
        wines = {w.id: w for w in Wine.objects.filter(id__in=wine_ids)}
        wines = [wines.get(id_) for id_ in wine_ids]
    else:
        wines = []
    return render_to_response(template_name="search_result.html", context={'wines': wines, "request": request})


def wine(request, wine_id):
   try:
       wines = [
           Wine.objects.get(id=wine_id)
       ]
   except Wine.DoesNotExist:
       wines = []
   return render_to_response(template_name="result.html", context={'wines': wines, 'one_wine_page': True})


def mobile_filtration(request):
    countries = [c.name for c in Country.objects.all()]
    return render_to_response(template_name="filtration.html", context={ "countries": countries,})


def filtration(request):
    categories = {}
    #country_list = request.GET.getlist('country')
    country = request.GET.get('country')
    if country:
        categories.update({'country__name': country})
    for category in ('color', 'type'):
        category_list = request.GET.getlist(category)
        if category_list: categories.update({category + '__in': category_list})
    for category in ('year__lt', 'year__gt', 'price__lt', 'price__gt'):
        c = request.GET.get(category)
        if c: categories.update({category: int(c)})
    #sort = request.GET.get('sort')
    #if sort: categories.update({'wine_to_sort__name': sort})
    wines = Wine.objects.select_related("country").filter(**categories)[:50]
    return render_to_response("filter_results.html", context={ "wines": wines})


def survey(request):
    if request.user.is_authenticated():
        feedback = Feedback.objects.get_last_review(request.user.id) 
        if feedback: return HttpResponseRedirect("/feedback")
        
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
    match_response = requests.get('/'.join((settings.MATCH_URL,"next")), params=params)
    
    if not match_response.status_code == 200:
        send_error_mail("next resonse return not 200 \n returned {}".format(match_response.text))
        return HttpResponseRedirect("/")
    match_response = json.loads(match_response.text)
    context = {
        "request": request
    }

    question = match_response.get("question")
    is_end = match_response.get("is_end")
    tries_count = 0
    q = None
    while tries_count < MAX_TRIES_COUNT:
        if is_end: break
        node = question["node"]
        try:
            q = Question.objects.get(node=node)
            break
        except Question.DoesNotExist:
            tries_count += 1

    if not is_end:
        if not q:
            send_error_mail("returned question is not find node: {}".format(question))
            return HttpResponseRedirect("/")
        context.update({
            "image": q.img,
            "text": q.get_question(),
            "answers": question['answers'],#q.get_answers(),
            "survey": current_survey
        })
        if len(context["answers"]) > 2:
            return render_to_response(template_name="survey.html", context=context)
        else:
            return render_to_response(template_name="yesno.html", context=context)
    else:
        match_response = requests.get('/'.join((settings.MATCH_URL,"wine_list", str(current_survey.pk))))
        if not match_response.status_code == 200:
            send_error_mail("next resonse return not 200 \n returned {}".format(match_response.text))
            return HttpResponseRedirect("/")
        match_response = json.loads(match_response.text)
        wines_list = match_response["wines"]
        wines = []
        for wine in wines_list:
            try:
                wines.append(Wine.objects.get(title=wine['title']))
            except Wine.DoesNotExist:
                pass #its ok to loose some wine
        context.update({"wines": wines})

        return render_to_response(template_name="result.html", context=context)


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


def survey_yesno(request):
    return render_to_response(template_name="yesno.html", context={"request":request})


def info(request):
    return render_to_response(template_name="about_us.html", context={"request":request})


def result(request):
    return render_to_response(template_name="result.html", context={"request":request})


def favorite(request):
    if request.user.is_authenticated():
        user = UserModel.objects.get(username=request.user)
        favorites = user.get_favorits()
        wines = [ w.wine for w in favorites]
        context = {
            "request": request,
            "wines": wines
        }
        return render_to_response(template_name="favorite.html", context=context)
    else:
        return HttpResponseForbidden()


def feedback(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    feed_back = Feedback.objects.get_last_review(request.user.id)
    if not feed_back:
        return HttpResponseRedirect("/")
    return render_to_response(template_name="feedbackform.html", context={"wine": feed_back.wine, "request": request})


def thnx_for_feedback(request):
    return render_to_response(
        template_name="thx_for_feedback.html", context={
            'declined_flag': request.GET.get('declined'),
            "request": request
        }
    )
