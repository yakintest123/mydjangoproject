# Generated by Django 3.0 on 2021-02-07 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_cancelappointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='reason_for_cancel',
            field=models.TextField(default=''),
        ),
    ]