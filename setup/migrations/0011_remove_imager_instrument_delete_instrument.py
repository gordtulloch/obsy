# Generated by Django 4.0.10 on 2024-06-24 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0010_alter_telescope_telescopetype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imager',
            name='instrument',
        ),
        migrations.DeleteModel(
            name='instrument',
        ),
    ]
