# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-29 18:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0020_sort'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sort',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='название сорта'),
        ),
    ]
