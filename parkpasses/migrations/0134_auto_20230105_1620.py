# Generated by Django 3.2.16 on 2023-01-05 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0133_alter_retailergroup_ledger_organisation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='retailergroup',
            name='address_line_1',
        ),
        migrations.RemoveField(
            model_name='retailergroup',
            name='address_line_2',
        ),
        migrations.RemoveField(
            model_name='retailergroup',
            name='postcode',
        ),
        migrations.RemoveField(
            model_name='retailergroup',
            name='state',
        ),
        migrations.RemoveField(
            model_name='retailergroup',
            name='suburb',
        ),
    ]
