# Generated by Django 3.2.13 on 2022-08-24 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0074_make_order_field_non_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='pass',
            name='postcode',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
