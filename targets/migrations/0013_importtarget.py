# Generated by Django 4.0.10 on 2024-10-02 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0012_rename_scheduleid_scheduledetail_schedulemasterid'),
    ]

    operations = [
        migrations.CreateModel(
            name='importTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='documents/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
