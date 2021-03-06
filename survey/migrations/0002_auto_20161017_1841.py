# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-17 18:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('survey', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='surveys', to=settings.AUTH_USER_MODEL, verbose_name='пользователь'),
        ),
        #migrations.AddField(
        #    model_name='favorites',
        #    name='user',
        #    field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
       # ),
        migrations.AddField(
            model_name='favorites',
            name='wine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Wine'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='survey.Question'),
        ),
    ]
