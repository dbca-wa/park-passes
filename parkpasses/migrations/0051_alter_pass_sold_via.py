# Generated by Django 3.2.13 on 2022-08-01 01:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0050_auto_20220728_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pass',
            name='sold_via',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.PROTECT, to='parkpasses.retailergroup'),
            preserve_default=False,
        ),
    ]
