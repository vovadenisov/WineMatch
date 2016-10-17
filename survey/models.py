# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.


class Survey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="surveys", verbose_name="пользователь", null=True, blank=True
    )


class Question(models.Model):
    question_text = models.CharField(max_length=250, unique=True, default='')
    node = models.CharField(max_length=250)
    gender = models.NullBooleanField(default=None)
    img = models.ImageField(default='korica.jpg', upload_to='img/')

    def get_node(self):
        return self.node

    def get_question(self):
        return self.question_text

    def get_answers(self):
        return self.answer_set.all()

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Wine(models.Model):
    color = models.CharField(max_length=10)
    type = models.CharField(max_length=50)
    description = models.CharField(max_length=2000)
    stylistic = models.CharField(max_length=1000)
    food = models.CharField(max_length=2000)
    alcohol = models.CharField(max_length=255, null=True)
    year = models.IntegerField(null=True)
    price = models.FloatField(default=0)
    title = models.CharField(max_length=255, unique=True)
    img = models.ImageField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def get_name(self):
        return self.title

    def get_country(self):
        return self.country.name

class Answer(models.Model):
    answer_text = models.CharField(max_length=100)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    api_response = models.IntegerField(default=0)
