# Generated by Django 4.2.7 on 2024-01-16 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("property", "0014_property_approval_status"),
        ("bookings", "0014_alter_bnbbooking_airbnb"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventspacebooking",
            name="event_space",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="eventspacebookings",
                to="property.property",
            ),
        ),
    ]
