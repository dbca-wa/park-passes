# Generated by Django 3.2.16 on 2023-02-01 01:45

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0154_remove_report_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='basket_id',
            field=models.IntegerField(default=239199),
        ),
        migrations.AddField(
            model_name='report',
            name='order_number',
            field=models.CharField(default='197284', max_length=128),
        ),
        migrations.AlterField(
            model_name='report',
            name='invoice_reference',
            field=models.CharField(default='28432634983', max_length=36),
        ),
        migrations.AlterField(
            model_name='report',
            name='uuid',
            field=models.CharField(default=uuid.UUID('c9bdde75-00a1-42cc-9dad-015f386d5f62'), max_length=36),
        ),
    ]
