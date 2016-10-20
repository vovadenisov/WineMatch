import json
import requests

from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response

from users.models import UserModel
from feedback.models import Feedback
from survey.models import Survey, Question, Wine


def main(request):
    return render_to_response(template_name="main.html", context={"request":request})


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
        try:
            q = Question.objects.get(node=node)
        except Question.DoesNotExist:
            print("Does Not Exist")
            return HttpResponseRedirect("/")
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
        u = UserModel.objects.get(username=request.user)
        favorites = u.get_favorits()
        context = {
            "request": request,
            "wines": favorites
        }
        return render_to_response(template_name="favorite.html", context=context)
    else:
        return HttpResponseForbidden()


def feedback(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    feedback = Feedback.objects.get_last_review(request.user.id) 
    if not feedback: return HttpResponseRedirect("/")
    return render_to_response(template_name="feedbackform.html", context={"wine": feedback.wine})


def thnx_for_feedback(request):
    return render_to_response(template_name="thx_for_feedback.html", context={'declined_flag': request.GET.get('declined')})
