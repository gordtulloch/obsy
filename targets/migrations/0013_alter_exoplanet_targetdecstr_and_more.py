# Generated by Django 5.1.4 on 2025-01-01 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0012_alter_exoplanet_targetdec2000_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exoplanet',
            name='targetDecStr',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='exoplanet',
            name='targetRAStr',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
