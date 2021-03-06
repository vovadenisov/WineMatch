from django.db import models, IntegrityError
from survey.models import Wine, Favorites


class FeedbackManager(models.Manager):
    def get_last_review(self, user_id):
        return self.filter(user__id=user_id).filter(has_declined=False).\
                    filter(has_answered=False).order_by('-created_at').first()      


class Feedback(models.Model):
    # логика ревью: в момент выбора пользователем вина созданем пустую модель ревью. 
    # Далее во вьюшке чекаем, есть ли пустые модели и показываем модалки для них.
    
    user = models.ForeignKey('users.UserModel', on_delete=models.CASCADE)
    wine = models.ForeignKey('survey.Wine', on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="Время выбора вина", auto_now_add=True)
    completed_at = models.DateTimeField(verbose_name="Время создания отзыва", null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    
    has_answered = models.BooleanField(verbose_name="Пользователь оставил отзыв", default=False)
    has_declined = models.BooleanField(verbose_name="Пользователь отказался осталвть отзыв", default=False)
    
    objects = FeedbackManager()
    
    def convert_to_fav(self):
        try:
            print(Favorites.objects.create(user = self.user, wine = self.wine, rating = self.rating))
        except IntegrityError as e:
            print(e)
            Favorites.objects.filter(user = self.user, wine = self.wine).update(rating = self.rating)
            
    def delete_fav_if_exists(self):
        Favorites.objects.filter(user = self.user, wine = self.wine).delete()
