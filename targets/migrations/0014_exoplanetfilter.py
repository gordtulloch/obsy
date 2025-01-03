# Generated by Django 5.1.4 on 2025-01-02 15:00

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0013_alter_exoplanet_targetdecstr_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExoplanetFilter',
            fields=[
                ('configId', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('min_transit_duration', models.FloatField(blank=True, null=True)),
                ('max_transit_duration', models.FloatField(blank=True, null=True)),
                ('min_depth', models.FloatField(blank=True, null=True)),
                ('max_depth', models.FloatField(blank=True, null=True)),
                ('min_altitude', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
