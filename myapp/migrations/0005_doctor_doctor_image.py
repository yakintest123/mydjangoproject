# Generated by Django 3.0 on 2020-12-26 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_auto_20201226_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='doctor_image',
            field=models.ImageField(default='', upload_to='images/'),
        ),
    ]
