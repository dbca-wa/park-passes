# Generated by Django 3.2.13 on 2022-07-12 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0041_auto_20220712_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='pass',
            name='in_cart',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='voucher',
            name='in_cart',
            field=models.BooleanField(default=True),
        ),
    ]