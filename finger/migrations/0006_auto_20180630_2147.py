# Generated by Django 2.0.6 on 2018-06-30 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finger', '0005_auto_20180630_1608'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='honourable_member',
            new_name='honorary_member',
        ),
    ]
