# Generated by Django 4.0.10 on 2024-06-28 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0011_rename_scheduleid_schedulemaster_schedulemasterid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scheduledetail',
            old_name='scheduleId',
            new_name='scheduleMasterId',
        ),
    ]
