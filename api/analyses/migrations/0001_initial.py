# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-09 21:55
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('datasets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_created=True, auto_now_add=True)),
                ('name', models.CharField(max_length=64)),
                ('params', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.Dataset')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_created=True, auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('value', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analyses.Analysis')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together=set([('analysis', 'name')]),
        ),
    ]
