# Generated by Django 3.2.13 on 2022-08-10 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0062_alter_faq_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='pass',
            name='drivers_licence_number',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
    ]