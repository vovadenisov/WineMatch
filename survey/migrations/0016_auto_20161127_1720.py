# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-27 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0015_wine_translit_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='wine',
            name='image2share',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Картинка вина'),
        ),
        migrations.AlterField(
            model_name='wine',
            name='translit_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Название транслитом'),
        ),
    ]
