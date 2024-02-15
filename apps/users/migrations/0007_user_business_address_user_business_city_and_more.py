# Generated by Django 4.2.7 on 2024-02-14 12:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_rename_postion_user_position"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="business_address",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="business_city",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="business_country",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="business_name",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="business_number",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
