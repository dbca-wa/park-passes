# Generated by Django 3.2.13 on 2022-07-28 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0048_discountcodebatch_datetime_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='discountcodebatch',
            name='created_by',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]