# Generated by Django 2.2.16 on 2020-11-15 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finger', '0008_auto_20201108_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
    ]
