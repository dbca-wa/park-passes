# Generated by Django 3.2.16 on 2022-12-20 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0125_passautorenewalattempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='pass',
            name='park_pass_renewed_from',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='renewed_pass', to='parkpasses.pass'),
        ),
        migrations.AlterField(
            model_name='pass',
            name='processing_status',
            field=models.CharField(blank=True, choices=[('CA', 'Cancelled'), ('AR', 'Awaiting Auto Renewal'), ('VA', 'Valid')], max_length=2, null=True),
        ),
    ]
