# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-17 04:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(max_length=100)),
                ('api_response', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(default='', max_length=250, unique=True)),
                ('node', models.CharField(max_length=250)),
                ('gender', models.NullBooleanField(default=None)),
                ('img', models.ImageField(default='korica.jpg', upload_to='img/')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='surveys', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='Wine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=10)),
                ('type', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=2000)),
                ('stylistic', models.CharField(max_length=1000)),
                ('food', models.CharField(max_length=2000)),
                ('alcohol', models.CharField(max_length=255, null=True)),
                ('year', models.IntegerField(null=True)),
                ('price', models.FloatField(default=0)),
                ('title', models.CharField(max_length=255, unique=True)),
                ('img', models.ImageField(upload_to='')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Country')),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='survey.Question'),
        ),
    ]
