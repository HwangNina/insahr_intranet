# Generated by Django 3.1.2 on 2020-11-21 06:43

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0003_auto_20201121_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 11, 21, 6, 43, 13, 126453, tzinfo=utc)),
        ),
    ]