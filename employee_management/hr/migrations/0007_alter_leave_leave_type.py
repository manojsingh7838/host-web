# Generated by Django 5.0.4 on 2024-06-20 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0006_rename_status_employee_martial_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leave',
            name='leave_type',
            field=models.CharField(choices=[('medical', 'medical'), ('sick', 'sick'), ('casual', 'casual')], max_length=10),
        ),
    ]