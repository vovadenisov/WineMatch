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
        answers = self.answer_set.all()


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="название страны")
    short_name = models.CharField(
        max_length=5, unique=True, null=True, blank=True, verbose_name="короткое название страны"
    )


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

class Favorites(models.Model):
    wine_attrs = {
        'color': 1,
        'type': 1,
        'description': 1,
        'stylistic': 1,
        'food': 1,
        'alcohol': 1,
        'year': 1,
        'price': 1,
        'title': 1,
        'img': 1,
        'country': 1,
    }
    
    user = models.ForeignKey('users.UserModel')
    wine = models.ForeignKey(Wine)
    rating = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'wine',)
        
    #грязный хак для отображения и вина и избранного в одном шаблоне
    def __getattr__(self, attr):
        if self.wine_attrs.get(attr): 
            #if attr == 'country': return self.wine.country.name
            return getattr(self.wine, attr)
        return super(Favorites, self).__getattr__(attr)
            
    @property
    def full_stars(self):
        return range(self.rating)
        
    @property
    def emplty_stars(self):
        return range(5 - self.rating)
