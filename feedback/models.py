from django.db import models

class FeedbackManager(models.Manager):
    def get_last_review(self, user_id):
        return self.filter(user__id=user_id).filter(has_declined=False).\
                    filter(has_answered=False).order_by('-created_at').first()      
                      
class Feedback(models.Model):
    # логика ревью: в момент выбора пользователем вина созданем пустую модель ревью. 
    # Далее во вьюшке чекаем, есть ли пустые модели и показываем модалки для них.
    
    user = models.ForeignKey('users.UserModel', on_delete=models.CASCADE)
    wine = models.ForeignKey('survey.Wine', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) #время выбора вина на ревью
    completed_at = models.DateTimeField() #время написания ревью
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    
    has_answered = models.BooleanField(default=False)
    has_declined = models.BooleanField(default=False)
    
    objects = FeedbackManager()
    
    
    