# Generated by Django 4.2.7 on 2024-02-07 06:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0018_payment_event_space_booking"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="payment_reason",
            field=models.CharField(
                choices=[
                    ("Room Booking", "Room Booking"),
                    ("AirBnB Booking", "AirBnB Booking"),
                    ("Ticket Booking", "Ticket Booking"),
                    ("Subscription", "Subscription"),
                    ("Event Space Booking", "Event Space Booking"),
                ],
                max_length=255,
            ),
        ),
    ]
