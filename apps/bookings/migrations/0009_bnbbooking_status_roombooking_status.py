# Generated by Django 4.2.7 on 2024-01-10 13:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0008_bnbbooking"),
    ]

    operations = [
        migrations.AddField(
            model_name="bnbbooking",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending Payment", "Pending Payment"),
                    ("Completed", "Completed"),
                    ("Cancelled", "Cancelled"),
                ],
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="roombooking",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending Payment", "Pending Payment"),
                    ("Completed", "Completed"),
                    ("Cancelled", "Cancelled"),
                ],
                max_length=255,
                null=True,
            ),
        ),
    ]
