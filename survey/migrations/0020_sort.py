# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-29 18:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0019_auto_20161128_2311'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='название сорта')),
            ],
            options={
                'verbose_name_plural': 'Сорт винограда',
                'verbose_name': 'Сорт винограда',
            },
        ),
    ]
