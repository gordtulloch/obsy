# Generated by Django 4.0.10 on 2024-03-25 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0004_observatory_remove_fitsfile_id_remove_fitsheader_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='instrument',
            name='instType',
            field=models.CharField(choices=[('AS', 'AllSkyCam'), ('WE', 'Weather Station')], default='', max_length=2),
            preserve_default=False,
        ),
    ]
