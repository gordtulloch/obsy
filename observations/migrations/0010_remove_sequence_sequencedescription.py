# Generated by Django 5.1.2 on 2024-11-10 23:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0009_remove_sequence_sequencename_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sequence',
            name='sequenceDescription',
        ),
    ]