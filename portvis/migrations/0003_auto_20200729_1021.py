# Generated by Django 3.0.8 on 2020-07-29 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portvis', '0002_auto_20200729_0859'),
    ]

    operations = [
        migrations.RenameField(
            model_name='action',
            old_name='date',
            new_name='tstamp',
        ),
        migrations.RenameField(
            model_name='price',
            old_name='date',
            new_name='tstamp',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='time',
            new_name='tstamp',
        ),
    ]
