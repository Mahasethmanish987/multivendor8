# Generated by Django 5.1.4 on 2024-12-07 21:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fooditem',
            old_name='is_availabe',
            new_name='is_available',
        ),
    ]
