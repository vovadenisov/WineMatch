# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-28 22:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0017_merge_20161127_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wine',
            name='image2share',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Картинка вина для шаринга'),
        ),
    ]