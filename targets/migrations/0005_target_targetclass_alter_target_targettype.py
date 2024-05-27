# Generated by Django 4.0.10 on 2024-05-21 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0004_rename_userid_target_userid'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='targetClass',
            field=models.CharField(choices=[('VS', 'Variable Star'), ('EX', 'Exoplanet'), ('DS', 'Deep Sky Object'), ('PL', 'Planet'), ('LU', 'Luna'), ('SU', 'Sun'), ('SA', 'Satellite'), ('OT', 'Other')], default='', max_length=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='target',
            name='targetType',
            field=models.CharField(max_length=255),
        ),
    ]
