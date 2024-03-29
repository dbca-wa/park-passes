# Generated by Django 3.2.13 on 2022-10-06 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0103_auto_20221004_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='retailergroup',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='retailergroupinvite',
            name='status',
            field=models.CharField(choices=[('N', 'New'), ('S', 'Sent'), ('ULI', 'User Logged In'), ('UA', 'User Accepted'), ('D', 'Denied'), ('A', 'Approved')], default='N', max_length=3),
        ),
    ]
