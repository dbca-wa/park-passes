# Generated by Django 3.2.16 on 2023-01-13 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0140_auto_20230113_0942'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('archive_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='passtypepricingwindowoption',
            options={'ordering': ['pricing_window', 'price'], 'verbose_name': 'Duration Option', 'verbose_name_plural': 'Duration Options'},
        ),
        migrations.AlterModelOptions(
            name='retailergroup',
            options={'ordering': ['ledger_organisation'], 'verbose_name': 'Retailer Group'},
        ),
        migrations.RemoveField(
            model_name='retailergroup',
            name='ledger_district',
        ),
        migrations.CreateModel(
            name='DistrictPassTypeDurationOracleCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ledger_district', models.IntegerField(default=1, verbose_name='Ledger District')),
                ('oracle_code', models.CharField(help_text='The oracle code to be used for this district, pass type and pass duration.', max_length=50)),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='district_oracle_code', to='parkpasses.passtypepricingwindowoption')),
            ],
            options={
                'verbose_name': 'District Based Oracle Code',
                'verbose_name_plural': 'District Based Oracle Codes',
                'unique_together': {('ledger_district', 'option')},
            },
        ),
    ]
