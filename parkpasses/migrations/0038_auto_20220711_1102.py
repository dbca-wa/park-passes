# Generated by Django 3.2.13 on 2022-07-11 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0037_alter_voucher_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pass',
            name='user',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='purchaser',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]