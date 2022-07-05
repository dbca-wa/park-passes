# Generated by Django 3.2.13 on 2022-07-05 02:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0033_auto_20220701_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucher',
            name='datetime_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='vouchertransaction',
            name='datetime_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vouchertransaction',
            name='datetime_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='passtypepricingwindow',
            name='pass_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pricing_window', to='parkpasses.passtype'),
        ),
        migrations.AlterField(
            model_name='passtypepricingwindowoption',
            name='pricing_window',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='option', to='parkpasses.passtypepricingwindow'),
        ),
    ]
