# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-18 05:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_auto_20161017_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]