# Generated by Django 5.1.5 on 2025-01-20 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0003_alter_observation_targetid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fitssequence',
            name='fitsSequenceThumbnailPath',
        ),
        migrations.AlterField(
            model_name='fitssequence',
            name='fitsSequenceDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
