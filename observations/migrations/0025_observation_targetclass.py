# Generated by Django 5.1.4 on 2024-12-18 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0024_fitssequence_fitssequencethumbnailpath'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='targetClass',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
