# Generated by Django 3.2.13 on 2022-08-11 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0064_discountcodebatchvalidpasstype_discountcodebatchvaliduser'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='discountcodebatchvalidpasstype',
            options={'verbose_name': 'Valid Pass Type'},
        ),
        migrations.AlterModelOptions(
            name='discountcodebatchvaliduser',
            options={'verbose_name': 'Valid User'},
        ),
        migrations.AlterField(
            model_name='discountcodebatch',
            name='times_each_code_can_be_used',
            field=models.SmallIntegerField(null=True),
        ),
    ]
