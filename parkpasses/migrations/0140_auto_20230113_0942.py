# Generated by Django 3.2.16 on 2023-01-13 01:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0139_alter_retailergroupuser_is_admin'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='retailergroup',
            options={'verbose_name': 'Retailer Group'},
        ),
        migrations.RemoveField(
            model_name='retailergroup',
            name='name',
        ),
    ]
