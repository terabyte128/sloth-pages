# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transfusion', '0003_course_short_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='short_description',
            field=models.TextField(null=True, max_length=500, blank=True),
        ),
    ]
