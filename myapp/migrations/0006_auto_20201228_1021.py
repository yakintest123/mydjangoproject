# Generated by Django 3.0 on 2020-12-28 04:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_doctor_doctor_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctor',
            old_name='drgree',
            new_name='degree',
        ),
    ]
