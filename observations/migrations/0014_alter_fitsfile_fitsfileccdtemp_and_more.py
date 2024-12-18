# Generated by Django 5.1.3 on 2024-11-08 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0013_alter_fitssequence_fitsmasterbias_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileCCDTemp',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileExpTime',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileGain',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileInstrument',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileName',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileObject',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileOffset',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileSequence',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileTelescop',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileType',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileXBinning',
            field=models.CharField(default='None', max_length=255),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='fitsFileYBinning',
            field=models.CharField(default='None', max_length=255),
        ),
    ]