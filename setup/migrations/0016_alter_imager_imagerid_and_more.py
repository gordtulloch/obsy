# Generated by Django 5.1.2 on 2024-10-09 23:15

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0015_alter_imager_imagerid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imager',
            name='imagerId',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='observatory',
            name='observatoryId',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='observer',
            name='observerId',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='telescope',
            name='telescopeId',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
