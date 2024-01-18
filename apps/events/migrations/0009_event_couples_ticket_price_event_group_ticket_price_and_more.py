# Generated by Django 4.2.7 on 2024-01-18 19:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0008_eventticket_notif_send_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="couples_ticket_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name="event",
            name="group_ticket_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name="event",
            name="students_ticket_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name="event",
            name="children_ticket_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name="event",
            name="regular_ticket_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name="event",
            name="vip_ticket_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name="event",
            name="vvip_ticket_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
    ]
