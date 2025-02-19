# Generated by Django 4.2.7 on 2024-01-03 18:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0006_alter_eventticketcomponent_ticket"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventticket",
            name="payment_link",
            field=models.URLField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name="eventticket",
            name="transaction_id",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="eventticket",
            name="tx_ref",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
