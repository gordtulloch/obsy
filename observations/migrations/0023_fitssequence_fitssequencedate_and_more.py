# Generated by Django 5.1.3 on 2024-11-24 23:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0022_alter_fitsfile_fitsfilesequence'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitssequence',
            name='fitsSequenceDate',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='fitssequence',
            name='fitsSequenceObjectName',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
