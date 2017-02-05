# -*- coding: utf-8 -*-
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, IntegrityError

from application.settings import MEDIA_ROOT
# Create your models here.


class Survey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="surveys", verbose_name="пользователь", null=True, blank=True
    )


class Question(models.Model):
    question_text = models.CharField(max_length=250, unique=True, default='', verbose_name="Текст вопроса")
    node = models.CharField(max_length=250, verbose_name="Нода для графа")
    gender = models.NullBooleanField(default=None, verbose_name="Пол юзера")
    img = models.ImageField(default='korica.jpg', upload_to='img/', verbose_name="Картинка")

    def get_node(self):
        return self.node

    def get_question(self):
        return self.question_text

    def get_answers(self):
        answers = self.answer_set.all()

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="название страны")
    short_name = models.CharField(
        max_length=5, unique=True, null=True, blank=True, verbose_name="короткое название страны"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class Group(models.Model):
    name = models.CharField(max_length=250, unique=True, verbose_name="название подборки")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Подборка вина"
        verbose_name_plural = "Подборка вина"

class Sort(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="название сорта")
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Сорт винограда"
        verbose_name_plural = "Сорт винограда"


class Wine(models.Model):
    color = models.CharField(max_length=10, verbose_name="Цвет")
    type = models.CharField(max_length=50, verbose_name="Сладость")
    description = models.CharField(max_length=2000, verbose_name="Подробное описание")
    stylistic = models.CharField(max_length=1000, verbose_name="Краткое описание")
    food = models.CharField(max_length=2000, verbose_name="Сочетающаяся еда", null=True)
    alcohol = models.CharField(max_length=255, null=True, verbose_name="Процент алкоголя")
    year = models.IntegerField(null=True, verbose_name="Год производства")
    price = models.FloatField(null=True, verbose_name="Цена")
    title = models.CharField(max_length=255, verbose_name="Название", unique=True)
    translit_title = models.CharField(max_length=255, verbose_name="Название транслитом", null=True, blank=True)
    img = models.ImageField(verbose_name="Картинка вина")
    image2share = models.ImageField(verbose_name="Картинка вина для шаринга", null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Страна")
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE, verbose_name="подборка вина")
    wine_to_sort = models.ManyToManyField(Sort, through='SortToWine')
    region = models.CharField(max_length=255, null=True, verbose_name="регион")

    def __init__(self, *args, **kwargs):
        s = super(Wine, self).__init__(*args, **kwargs)
        self._is_in_fav = False
        return s

    @property
    def is_in_fav(self):
        return self._is_in_fav

    @is_in_fav.setter
    def is_in_fav(self, value):
        self._is_in_fav = value
        return value

    @property
    def absolute_img_path(self):
        return "{0}/..{1}".format(MEDIA_ROOT, self.img.url)

    def get_shops(self):
        return self.winetoshop_set.all()
        # return [s.shop for s in shops]

    def get_name(self):
        return self.title

    def get_country(self):
        return self.country.name

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вино"
        verbose_name_plural = "Вина"


class Answer(models.Model):
    #answer_text = models.CharField(max_length=100, verbose_name="Текст ответа")
    #question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, verbose_name="Вопрос")
    api_node = models.CharField(verbose_name="Node", max_length=255)
    api_answer_id = models.IntegerField(default=0, verbose_name="Ответ РС")
    image = models.ImageField(verbose_name="Image for answer")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        unique_together = ('api_node', 'api_answer_id')


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

    user = models.ForeignKey('users.UserModel', verbose_name="Пользователь")
    wine = models.ForeignKey(Wine, verbose_name="Вино")
    rating = models.IntegerField(default=0, verbose_name="Оценка от пользователя")

    class Meta:
        unique_together = ('user', 'wine',)
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    # грязный хак для отображения и вина и избранного в одном шаблоне
    def __getattr__(self, attr):
        if self.wine_attrs.get(attr):
            return getattr(self.wine, attr)
        return super(Favorites, self).__getattr__(attr)

    @property
    def full_stars(self):
        return range(self.rating)

    @property
    def emplty_stars(self):
        return range(5 - self.rating)


class Recommended(models.Model):
    user = models.ForeignKey('users.UserModel', verbose_name="Пользователь")
    wine = models.ForeignKey(Wine, verbose_name="Вино")

    class Meta:
        unique_together = ('user', 'wine',)
        verbose_name = "Рекомендованное"
        verbose_name_plural = "Рекрмендованное"


ANSWER_TYPE_CHOICES = (('json', 'json'), ('html', 'html'))


class WineShop(models.Model):
    code = models.CharField(verbose_name='Для выбора метода-парсера в краулере', max_length=30)
    name = models.CharField(verbose_name='Название магазина', max_length=255)
    photo = models.ImageField(upload_to='img/')
    search_url = models.CharField(verbose_name='Урл для поиска', max_length=255)
    answer_type = models.CharField(verbose_name='Тип ответа (json/html)', max_length=10, choices=ANSWER_TYPE_CHOICES)
    base_url = models.CharField(verbose_name='Базовый урл', max_length=255)

    def form_query(self, query_string):
        query_string = quote(query_string)
        return self.search_url.format(query_string)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазин'


class WineToShopManager(models.Manager):
    def _form_url_inplace(self, kwargs):
        if not kwargs.get('url').startswith(kwargs.get('shop').base_url):
            kwargs['url'] = kwargs.get('shop').base_url + kwargs.get('url')

    def create_or_update(self, **kwargs):
        self._form_url_inplace(kwargs)

        try:
            return self.create(**kwargs)
        except IntegrityError:
            self.filter(wine__id=kwargs['wine'].id).filter(shop__id=kwargs.get('shop').id).update(**kwargs)
            return self.get(wine__id=kwargs['wine'].id, shop__id=kwargs.get('shop').id)


class WineToShop(models.Model):
    # wine, shop, price, url
    wine = models.ForeignKey(Wine, verbose_name='Вино')
    shop = models.ForeignKey(WineShop, verbose_name='Магазин')
    price = models.IntegerField(verbose_name='Цена')
    url = models.CharField(verbose_name='Ссылка на товар', max_length=255)

    objects = WineToShopManager()

    def __str__(self):
        return '{}--{}'.format(self.wine.title, self.shop.name)

    class Meta:
        verbose_name = "Вино в магазине"
        verbose_name_plural = "Вина в магазине"


class SortToWine(models.Model):
    wine = models.ForeignKey(Wine, verbose_name='Вино')
    sort = models.ForeignKey(Sort, verbose_name='Сорт')
