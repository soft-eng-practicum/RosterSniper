# Generated by Django 4.1.1 on 2022-10-27 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='military_time',
            field=models.BooleanField(default=False, help_text='Whether the 24hr time format is enabled'),
        ),
        migrations.AddField(
            model_name='user',
            name='sms_notify',
            field=models.BooleanField(default=False, help_text='Whether the user should recieve sms messages'),
        ),
    ]