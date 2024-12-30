# Generated by Django 5.1.4 on 2024-12-30 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targets', '0002_alter_target_targetclass'),
    ]

    operations = [
        migrations.CreateModel(
            name='NasaExplanetArchive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kepid', models.CharField(blank=True, max_length=255, null=True)),
                ('kepoi_name', models.CharField(blank=True, max_length=255, null=True)),
                ('kepler_name', models.CharField(blank=True, max_length=255, null=True)),
                ('koi_disposition', models.CharField(blank=True, max_length=255, null=True)),
                ('koi_pdisposition', models.CharField(blank=True, max_length=255, null=True)),
                ('koi_score', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_fpflag_nt', models.BooleanField(blank=True, max_length=255, null=True)),
                ('koi_fpflag_ss', models.BooleanField(blank=True, max_length=255, null=True)),
                ('koi_fpflag_co', models.BooleanField(blank=True, max_length=255, null=True)),
                ('koi_fpflag_ec', models.BooleanField(blank=True, max_length=255, null=True)),
                ('koi_period', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_period_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_period_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_time0bk', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_time0bk_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_time0bk_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_impact', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_impact_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_impact_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_duration', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_duration_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_duration_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_depth', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_depth_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_depth_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_prad', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_prad_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_prad_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_teq', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_teq_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_teq_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_insol', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_insol_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_insol_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_model_snr', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_tce_plnt_num', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_tce_delivname', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_steff', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_steff_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_steff_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_slogg', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_slogg_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_slogg_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_srad', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_srad_err1', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_srad_err2', models.FloatField(blank=True, max_length=255, null=True)),
                ('ra', models.FloatField(blank=True, max_length=255, null=True)),
                ('dec', models.FloatField(blank=True, max_length=255, null=True)),
                ('koi_kepmag', models.FloatField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
