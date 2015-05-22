# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transfusion', '0002_teacherprofile_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='short_description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
