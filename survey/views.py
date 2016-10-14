import json

from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import requests


# Create your views here.
from survey.models import Survey


def main(request):
    return render_to_response(template_name="main.html", context={"request":request})


def survey(request):

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
                return render_to_response(template_name="yesno.html", context=context)


def survey_yesno(request):
    return render_to_response(template_name="yesno.html", context={"request":request})


def info(request):
    return render_to_response(template_name="about_us.html", context={"request":request})


def result(request):
    return render_to_response(template_name="result.html", context={"request":request})


def favorite(request):
    return render_to_response(template_name="favorite.html", context={"request":request})
