# Generated by Django 3.2.16 on 2022-11-16 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0121_remove_pass_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pass',
            name='processing_status',
            field=models.CharField(blank=True, choices=[('CA', 'Cancelled'), ('VA', 'Valid')], max_length=2, null=True),
        ),
        migrations.DeleteModel(
            name='UserInformation',
        ),
    ]
