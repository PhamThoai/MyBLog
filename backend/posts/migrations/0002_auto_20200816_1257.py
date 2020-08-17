# Generated by Django 3.0.8 on 2020-08-16 05:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_of', to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
        migrations.AlterField(
            model_name='post',
            name='publish_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publish', to=settings.AUTH_USER_MODEL, verbose_name='publishing manager'),
        ),
        migrations.AlterField(
            model_name='post',
            name='read_time',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='read time'),
        ),
        migrations.AlterField(
            model_name='post',
            name='views',
            field=models.IntegerField(default=0, verbose_name='views'),
        ),
    ]