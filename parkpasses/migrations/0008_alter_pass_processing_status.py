# Generated by Django 3.2.13 on 2022-06-20 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0007_alter_pass_park_pass_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pass',
            name='processing_status',
            field=models.CharField(blank=True, choices=[('FU', 'Future'), ('CU', 'Current'), ('EX', 'Expired'), ('CA', 'Cancelled')], max_length=2, null=True),
        ),
    ]
