# Generated by Django 5.1.3 on 2024-11-07 22:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0015_remove_scheduledetail_schedulemasterid_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='importTarget',
        ),
    ]
