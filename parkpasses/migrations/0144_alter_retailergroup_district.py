# Generated by Django 3.2.16 on 2023-01-13 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0143_auto_20230113_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailergroup',
            name='district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='retailer_group', to='parkpasses.district'),
        ),
    ]
