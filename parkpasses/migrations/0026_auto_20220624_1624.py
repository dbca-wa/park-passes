# Generated by Django 3.2.13 on 2022-06-24 08:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0025_alter_park_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='park',
            unique_together=set(),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_order', models.SmallIntegerField()),
                ('park', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parkpasses.park')),
                ('park_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parkpasses.parkgroup')),
            ],
            options={
                'unique_together': {('park_group', 'display_order')},
            },
        ),
        migrations.RemoveField(
            model_name='park',
            name='display_order',
        ),
        migrations.RemoveField(
            model_name='park',
            name='park_group',
        ),
        migrations.AddField(
            model_name='parkgroup',
            name='parks',
            field=models.ManyToManyField(blank=True, related_name='park_groups', through='parkpasses.Member', to='parkpasses.Park'),
        ),
    ]