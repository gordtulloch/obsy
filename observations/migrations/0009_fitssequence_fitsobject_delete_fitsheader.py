# Generated by Django 5.1.3 on 2024-11-08 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0008_observation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitssequence',
            name='fitsObject',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='fitsHeader',
        ),
    ]