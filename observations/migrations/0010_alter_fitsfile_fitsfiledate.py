# Generated by Django 5.1.6 on 2025-02-09 20:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0009_alter_fitsfile_fitsfiledate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileDate',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 9, 14, 8, 31, 601739, tzinfo=datetime.timezone.utc)),
        ),
    ]
