# Generated by Django 5.1.4 on 2024-12-09 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0017_target_targetdefaultthumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='Target',
            name='targetDefaultThumbnail',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]