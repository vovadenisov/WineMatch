from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.http import HttpResponseNotAllowed, HttpResponseForbidden, JsonResponse
from django.views.generic import ListView

from feedback.models import Feedback
from survey.models import Wine

FAV_TRESHOLD = 3


def _validate_request_method(request):
    if request.method != "POST": return HttpResponseNotAllowed('Only POST here')
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
    data = {key: post_params.get(key) for key in ['rating', 'comment'] if post_params.get(key)}
    try:
        data['rating'] = int(data['rating'])
    except (ValueError, TypeError):
        return None, ['rating']
    return data, None


def _ok_json():
    return JsonResponse({'result': True}) 


def answer_review(request):
    err = _validate_request_method(request)
    if err: return err
    
    review = Feedback.objects.get_last_review(request.user.id)
    if not review: return _error_json('Нет выборок для ревью')
    
    data4update, error_fields = _validate_review_form(request.POST)
    if error_fields: return _error_json('Заполните все обязательные поля', fields=error_fields)
    data4update.update({'has_answered': True, 'completed_at': timezone.now()})
      
    Feedback.objects.filter(id = review.id).update(**data4update)
    if data4update['rating'] > FAV_TRESHOLD:
        review.rating = data4update['rating'] 
        review.convert_to_fav() 
    else:
        review.delete_fav_if_exists()
        
    return _ok_json()


def decline_review(request):
    err = _validate_request_method(request)
    if err: return err
    
    review = Feedback.objects.get_last_review(request.user.id)
    if not review: return _error_json('Нет выборок для ревью')

    Feedback.objects.filter(id = review.id).update(completed_at=timezone.now(), has_declined = True)
    
    return _ok_json()
        

def select_wine4review(request):
    err = _validate_request_method(request)
    if err: return err
    
    wine = Wine.objects.filter(id=request.POST.get('wine_id')).first()
    if not wine: return _error_json('Нет такого вина')
    
    Feedback.objects.create(user=request.user, wine=wine)
    return _ok_json()


class Recommended(ListView):
    model = Feedback
    template_name = "favorite.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        filtered_wines = set()
        for feedback in queryset:
            filtered_wines.add(feedback.wine)
        print(filtered_wines)
        return list(filtered_wines)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        context["wines"] = context["object_list"]
        context["recommended"] = True
        return context
