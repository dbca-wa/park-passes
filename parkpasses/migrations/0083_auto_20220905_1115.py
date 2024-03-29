# Generated by Django 3.2.13 on 2022-09-05 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0082_alter_pass_mobile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='uuid',
            field=models.CharField(help_text='This is copied from the cart to the order before the cart is deleted.             It is also stored in ledger as the booking reference of the basket.', max_length=36),
        ),
        migrations.AlterField(
            model_name='pass',
            name='datetime_expiry',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='pass',
            name='datetime_start',
            field=models.DateField(),
        ),
        migrations.AlterUniqueTogether(
            name='helptext',
            unique_together={('label', 'version')},
        ),
    ]
