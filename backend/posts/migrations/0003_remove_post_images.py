# Generated by Django 3.0.8 on 2020-08-17 01:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20200816_1257'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='images',
        ),
    ]
