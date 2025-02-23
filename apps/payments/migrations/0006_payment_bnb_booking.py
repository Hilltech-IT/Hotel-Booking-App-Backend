# Generated by Django 4.2.7 on 2024-01-04 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0008_bnbbooking"),
        ("payments", "0005_payment_payment_link_payment_transaction_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="bnb_booking",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bnbbookingpayments",
                to="bookings.bnbbooking",
            ),
        ),
    ]
