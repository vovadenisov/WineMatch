from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.


class Survey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="surveys", verbose_name="пользователь", null=True, blank=True
    )
