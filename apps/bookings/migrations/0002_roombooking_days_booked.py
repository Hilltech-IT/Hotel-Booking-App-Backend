# Generated by Django 4.2.7 on 2023-12-20 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='roombooking',
            name='days_booked',
            field=models.IntegerField(default=0),
        ),
    ]
