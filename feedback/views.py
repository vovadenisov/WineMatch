from datetime import datetime

from django.shortcuts import render_to_response
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, JsonResponse

from feedback.models import Feedback
from survey.models import Wine

def _validate_request_method(request):
    if request.method != "POST": return HttpResponseNotAllowed()
    if not request.user.is_authenticated(): return HttpResponseForbidden()
 
def _error_json(message, **kwargs):
    res = {'result': False, 'message': message}
    res.update(kwargs)
    return JsonResponse(
        res,
        safe=False
    )  

def _validate_review_form(post_params):
    if not post_params.get('rating'): return None, ['rating']
    return {key: post_params.get(key) for key in ['rating', 'comment'] if post_params.get(key)}, None
    
def _ok_json():
    return JsonResponse({'result': True}) 
     
def answer_review(request):
    err = _validate_request_method(request)
    if err: return err
    
    review = Feedback.objects.get_last_review(request.user.id)
    if not review: return _error_json('Нет выборок для ревью')
    
    data4update, error_fields = _validate_review_form(request.POST)
    if error_fields: return _error_json('Заполните все обязательные поля', fields=error_fields)
    data4update.update({'has_answered': True, 'completed_at': datetime.now()})
      
    Feedback.objects.filter(id = review.id).update(**data4update)
    
    return _ok_json()
    
def decline_review(request):
    err = _validate_request_method(request)
    if err: return err
    
    review = Feedback.objects.get_last_review(request.user.id)
    if not review: return _error_json('Нет выборок для ревью')

    Feedback.objects.filter(id = review.id).update(completed_at = datetime.now(), has_declined = True)
    
    return _ok_json()
        
def select_wine4review(request):
    err = _validate_request_method(request)
    if err: return err
    
    wine = Wine.objects.filter(id=request.POST.get('wine_id')).first()
    if not wine: return _error_json('Нет такого вина')
    
    Feedback.objects.create(user=request.user, wine=wine)
    return _ok_json()
  