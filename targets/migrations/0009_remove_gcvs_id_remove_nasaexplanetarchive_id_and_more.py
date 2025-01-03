# Generated by Django 5.1.4 on 2024-12-31 20:02

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0008_alter_gcvs_dec_alter_gcvs_ra'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gcvs',
            name='id',
        ),
        migrations.RemoveField(
            model_name='nasaexplanetarchive',
            name='id',
        ),
        migrations.AddField(
            model_name='gcvs',
            name='targetId',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='nasaexplanetarchive',
            name='targetId',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]