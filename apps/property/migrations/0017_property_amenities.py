# Generated by Django 4.2.7 on 2024-01-16 21:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("property", "0016_property_adults_allowed_property_children_allowed"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="amenities",
            field=models.JSONField(default=list),
        ),
    ]
