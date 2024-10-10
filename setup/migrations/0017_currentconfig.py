# Generated by Django 5.1.2 on 2024-10-10 17:24

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0016_alter_imager_imagerid_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='currentConfig',
            fields=[
                ('currentConfigId', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('imagerId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='setup.imager')),
                ('observatoryId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='setup.observatory')),
                ('telescopeId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='setup.telescope')),
            ],
        ),
    ]
