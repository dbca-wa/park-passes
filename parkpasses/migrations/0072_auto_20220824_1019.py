# Generated by Django 3.2.13 on 2022-08-24 02:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('parkpasses', '0071_auto_20220824_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='invoice_reference',
            field=models.CharField(help_text='This links the order to the matching invoice in ledger.', max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='uuid',
            field=models.CharField(help_text='This is copied from the cart to the order before the cart is deleted.', max_length=36),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='object_id',
            field=models.CharField(max_length=191),
        ),
    ]
