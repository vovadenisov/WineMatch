# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-30 09:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0021_auto_20161129_1822'),
    ]

    operations = [
        migrations.CreateModel(
            name='SortToWine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Sort', verbose_name='Сорт')),
                ('wine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Wine', verbose_name='Вино')),
            ],
        ),
    ]
