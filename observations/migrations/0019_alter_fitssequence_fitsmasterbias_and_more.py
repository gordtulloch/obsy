# Generated by Django 5.1.3 on 2024-11-22 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0018_alter_schedulemaster_imagerid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitssequence',
            name='fitsMasterBias',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='fitssequence',
            name='fitsMasterDark',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='fitssequence',
            name='fitsMasterFlat',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='fitssequence',
            name='fitsObject',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
