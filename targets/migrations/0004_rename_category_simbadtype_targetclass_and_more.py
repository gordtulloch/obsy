# Generated by Django 5.1.4 on 2024-12-30 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0003_nasaexplanetarchive'),
    ]

    operations = [
        migrations.RenameField(
            model_name='simbadtype',
            old_name='category',
            new_name='targetClass',
        ),
        migrations.AlterField(
            model_name='nasaexplanetarchive',
            name='koi_tce_delivname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
