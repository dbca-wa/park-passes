# Generated by Django 3.2.16 on 2023-01-12 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0135_order_payment_confirmed'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkgroup',
            name='oracle_code',
            field=models.CharField(default='PARKPASSES_DEFAULT_ORACLE_CODE', max_length=50),
        ),
    ]
