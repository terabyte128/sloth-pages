# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transfusion', '0004_auto_20150521_1702'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField(null=True, blank=True)),
                ('filename', models.TextField()),
                ('course', models.ForeignKey(to='transfusion.Course')),
            ],
        ),
    ]
