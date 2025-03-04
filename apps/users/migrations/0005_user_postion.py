# Generated by Django 4.2.7 on 2023-11-29 05:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_user_city"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="postion",
            field=models.CharField(
                choices=[
                    ("CEO", "Chief Executive Officer"),
                    ("CIO", "Chief Information Officer"),
                    ("CTO", "Chief Technology Officer"),
                    ("COO", "Chief Operating Officer"),
                    ("CFO", "Chief Finance Officer"),
                    ("DCP", "Director Corporate And Business"),
                    ("DCSA", "Director Client Services And Administration"),
                ],
                max_length=255,
                null=True,
            ),
        ),
    ]
