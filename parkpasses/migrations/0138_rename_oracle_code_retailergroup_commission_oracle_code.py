# Generated by Django 3.2.16 on 2023-01-13 01:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0137_auto_20230113_0900'),
    ]

    operations = [
        migrations.RenameField(
            model_name='retailergroup',
            old_name='oracle_code',
            new_name='commission_oracle_code',
        ),
    ]
