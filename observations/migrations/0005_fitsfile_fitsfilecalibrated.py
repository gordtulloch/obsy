# Generated by Django 5.1.2 on 2024-10-27 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0004_fitsfile_remove_scheduledetail_schedulemasterid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitsfile',
            name='fitsFileCalibrated',
            field=models.BooleanField(default=False),
        ),
    ]