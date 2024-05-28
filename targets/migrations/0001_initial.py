# Generated by Django 4.0.10 on 2024-05-28 20:16

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='simbadType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='target',
            fields=[
                ('targetId', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('userId', models.CharField(max_length=255)),
                ('targetName', models.CharField(max_length=255)),
                ('catalogIDs', models.CharField(max_length=255)),
                ('targetClass', models.CharField(choices=[('VS', 'Variable Star'), ('EX', 'Exoplanet'), ('DS', 'Deep Sky Object'), ('PL', 'Planet'), ('LU', 'Luna'), ('SU', 'Sun'), ('SA', 'Satellite'), ('OT', 'Other')], max_length=2)),
                ('targetType', models.CharField(max_length=255)),
                ('targetRA2000', models.CharField(max_length=200)),
                ('targetDec2000', models.CharField(max_length=200)),
                ('targetConst', models.CharField(max_length=200)),
                ('targetMag', models.CharField(max_length=200)),
            ],
        ),
    ]
