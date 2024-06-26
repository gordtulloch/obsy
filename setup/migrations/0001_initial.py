# Generated by Django 4.0.10 on 2024-03-12 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='openNGC',
            fields=[
                ('id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=200)),
                ('ra', models.CharField(max_length=200)),
                ('dec', models.CharField(max_length=200)),
                ('const', models.CharField(max_length=200)),
                ('majax', models.CharField(max_length=200)),
                ('minax', models.CharField(max_length=200)),
                ('pa', models.CharField(max_length=200)),
                ('bmag', models.CharField(max_length=200)),
                ('vmag', models.CharField(max_length=200)),
                ('jmag', models.CharField(max_length=200)),
                ('hmag', models.CharField(max_length=200)),
                ('kmag', models.CharField(max_length=200)),
                ('sbrightn', models.CharField(max_length=200)),
                ('hubble', models.CharField(max_length=200)),
                ('parallax', models.CharField(max_length=200)),
                ('pmra', models.CharField(max_length=200)),
                ('pmdec', models.CharField(max_length=200)),
                ('radvel', models.CharField(max_length=200)),
                ('redshift', models.CharField(max_length=200)),
                ('cstarumag', models.CharField(max_length=200)),
                ('cstarbmag', models.CharField(max_length=200)),
                ('cstarvmag', models.CharField(max_length=200)),
                ('messier', models.CharField(max_length=200)),
                ('ngc', models.CharField(max_length=200)),
                ('ic', models.CharField(max_length=200)),
                ('cstarnames', models.CharField(max_length=200)),
                ('identifiers', models.CharField(max_length=200)),
                ('commonnames', models.CharField(max_length=200)),
                ('nednotes', models.CharField(max_length=200)),
                ('ongcnotes', models.CharField(max_length=200)),
                ('notngc', models.CharField(max_length=200)),
            ],
        ),
    ]
