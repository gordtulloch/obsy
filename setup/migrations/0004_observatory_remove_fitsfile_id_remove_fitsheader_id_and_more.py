# Generated by Django 4.0.10 on 2024-03-12 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0003_alter_fitsheader_parentunid'),
    ]

    operations = [
        migrations.CreateModel(
            name='observatory',
            fields=[
                ('thisUNID', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('shortname', models.CharField(max_length=200)),
                ('latitude', models.DecimalField(decimal_places=2, max_digits=6)),
                ('longitude', models.DecimalField(decimal_places=2, max_digits=6)),
                ('tz', models.CharField(max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='fitsfile',
            name='id',
        ),
        migrations.RemoveField(
            model_name='fitsheader',
            name='id',
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='fitsfile',
            name='thisUNID',
            field=models.CharField(max_length=200, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='fitsheader',
            name='thisUNID',
            field=models.CharField(max_length=200, primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='telescope',
            fields=[
                ('thisUNID', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('shortname', models.CharField(max_length=200)),
                ('aperture', models.DecimalField(decimal_places=2, max_digits=6)),
                ('focalLength', models.DecimalField(decimal_places=2, max_digits=6)),
                ('observatory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='setup.observatory')),
            ],
        ),
        migrations.CreateModel(
            name='observer',
            fields=[
                ('thisUNID', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('firstname', models.CharField(max_length=200)),
                ('middlename', models.CharField(max_length=200)),
                ('lastname', models.CharField(max_length=200)),
                ('tz', models.CharField(max_length=200)),
                ('observatory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='setup.observatory')),
            ],
        ),
        migrations.CreateModel(
            name='instrument',
            fields=[
                ('thisUNID', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('shortname', models.CharField(max_length=200)),
                ('observatory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='setup.observatory')),
            ],
        ),
        migrations.CreateModel(
            name='imager',
            fields=[
                ('thisUNID', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('shortname', models.CharField(max_length=200)),
                ('xDim', models.DecimalField(decimal_places=0, max_digits=5)),
                ('yDim', models.DecimalField(decimal_places=0, max_digits=5)),
                ('xPixelSize', models.DecimalField(decimal_places=2, max_digits=6)),
                ('yPixelSize', models.DecimalField(decimal_places=2, max_digits=6)),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='setup.instrument')),
            ],
        ),
    ]