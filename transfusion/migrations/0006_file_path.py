# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transfusion', '0005_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='path',
            field=models.TextField(default='/'),
            preserve_default=False,
        ),
    ]
