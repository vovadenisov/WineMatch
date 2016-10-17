import json

from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from users.models import UserModel
import requests


# Create your views here.
from survey.models import Survey, Question, Wine

def main(request):
    return render_to_response(template_name="main.html", context={"request":request})

'''def survey(request):

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
            return HttpResponseRedirect("/")
    params = {
        "user_id": current_survey.pk,
    }
    print(params)
    if answer_pk:
        params.update({"answer_id": answer_pk})
    print(settings.MATCH_URL)
    match_response = requests.get(settings.MATCH_URL, params=params)
    print(match_response.text)
    if not match_response.status_code == 200:
        return HttpResponseRedirect("/")
    match_response = json.loads(match_response.text)
    context = {
        "request": request
    }
    if match_response.get("wine"):
        wines = match_response.get("wines")
        context.update({"wines": wines})
        return render_to_response(template_name="result.html", context=context)
    else:
        question = match_response["question"]
        if question:
            answers = question["answers"]
            context.update({
                "text": question["text"],
                "answers": answers,
                "survey": current_survey
            })
            if len(context["answers"]) > 2:
                return render_to_response(template_name="survey.html", context=context)
            else:
                return render_to_response(template_name="yesno.html", context=context)'''

def survey(request):
    answer_pk = request.GET.get("answer")
    print(answer_pk)
    if not answer_pk:
        print("create_survey")
        survey_context = {}
        if request.user.is_authenticated():
            survey_context.update({"user": request.user})
        current_survey = Survey.objects.create(**survey_context)
    else:
        print("get_survey")
        if request.GET.get("survey"):
            current_survey = Survey.objects.get(pk=request.GET.get("survey"))
        else:
            return HttpResponseRedirect("/")
    params = {
        "user_id": current_survey.pk,
    }
    if answer_pk:
        params.update({"answer_id": answer_pk})
    match_response = requests.get('/'.join((settings.MATCH_URL,"next")), params=params)
    
    if not match_response.status_code == 200:
        return HttpResponseRedirect("/")
    match_response = json.loads(match_response.text)
    context = {
        "request": request
    }
    question = match_response["question"]
    is_end = match_response["is_end"]
    if not is_end:
        node = question["node"]
        q = Question.objects.get(node=node)
        context.update({
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
    "price": 1000,
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
    print('faborite')
    if request.user.is_authenticated():
        print(request.user)
        u = UserModel.objects.get(username=request.user)
        favorites = u.get_favorits()
        wines = [f.wine for f in favorites]
        context = {
            "request": request,
            "wines": wines
        }
        return render_to_response(template_name="favorite.html", context=context)
    else:
        return HttpResponseForbidden()

