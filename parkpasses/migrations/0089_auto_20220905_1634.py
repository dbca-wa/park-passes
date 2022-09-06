# Generated by Django 3.2.13 on 2022-09-05 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0088_concessionusage_discountcodeusage_vouchertransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='concession_usage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='parkpasses.concessionusage'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='discount_code_usage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='parkpasses.discountcodeusage'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='voucher_transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='parkpasses.vouchertransaction'),
        ),
    ]
