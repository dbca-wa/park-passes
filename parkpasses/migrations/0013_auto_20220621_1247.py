# Generated by Django 3.2.13 on 2022-06-21 04:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0012_auto_20220621_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='datetime_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cart',
            name='datetime_first_added_to',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
