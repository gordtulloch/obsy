# Generated by Django 5.1.4 on 2024-12-24 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='target',
            name='targetClass',
            field=models.CharField(choices=[('VS', 'Variable Star'), ('EX', 'Exoplanet'), ('DS', 'Deep Sky Object'), ('PL', 'Planet'), ('LU', 'Luna'), ('SU', 'Sun'), ('SA', 'Satellite'), ('OT', 'Other')], default='DS', max_length=255),
        ),
    ]
