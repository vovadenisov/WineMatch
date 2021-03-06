# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-20 17:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0009_auto_20161019_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wine',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterUniqueTogether(
            name='wine',
            unique_together=set([('title', 'year')]),
        ),
    ]
