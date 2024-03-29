# Generated by Django 3.2.13 on 2022-06-23 02:14

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0017_alter_passtemplate_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=50, unique=True)),
                ('content', ckeditor.fields.RichTextField()),
                ('version', models.SmallIntegerField(default=1)),
            ],
        ),
    ]
