# Generated by Django 5.1.5 on 2025-01-18 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0002_observation_targetname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='targetId',
            field=models.UUIDField(default='00000000-0000-0000-0000-000000000000'),
            preserve_default=False,
        ),
    ]
