# Generated by Django 3.2.3 on 2021-05-23 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smartgarden', '0004_auto_20210522_1146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='circuit',
            name='owner',
        ),
    ]
