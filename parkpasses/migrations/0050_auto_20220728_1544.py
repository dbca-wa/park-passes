# Generated by Django 3.2.13 on 2022-07-28 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0049_discountcodebatch_created_by'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DayEntryPass',
        ),
        migrations.DeleteModel(
            name='GoldStarPass',
        ),
        migrations.DeleteModel(
            name='HolidayPass',
        ),
        migrations.DeleteModel(
            name='LocalParkPass',
        ),
        migrations.RemoveField(
            model_name='pass',
            name='park',
        ),
        migrations.AddField(
            model_name='pass',
            name='park_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='parkpasses.parkgroup'),
        ),
    ]