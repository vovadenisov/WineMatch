# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-19 08:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_auto_20161018_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='short_name',
            field=models.CharField(blank=True, max_length=5, null=True, unique=True),
        ),
    ]
