# Generated by Django 3.2.13 on 2022-09-07 06:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0089_auto_20220905_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='datetime_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
