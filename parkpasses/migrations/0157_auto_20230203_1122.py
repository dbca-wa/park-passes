# Generated by Django 3.2.16 on 2023-02-03 03:22

from django.db import migrations, models
import parkpasses.components.reports.models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0156_auto_20230201_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='uuid',
            field=models.CharField(default="", help_text='This is used as the booking reference for the generated ledger invoice.', max_length=36, unique=True),
        ),
        migrations.DeleteModel(
            name='RetailerGroupAPIKey',
        ),
    ]
