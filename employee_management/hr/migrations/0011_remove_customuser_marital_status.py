# Generated by Django 5.0.4 on 2024-06-21 03:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0010_rename_account_customuser_account_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='marital_status',
        ),
    ]
