# Generated by Django 4.2.7 on 2023-12-13 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0003_room_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propertyroom',
            name='bed_type',
        ),
        migrations.RemoveField(
            model_name='propertyroom',
            name='floor_level',
        ),
        migrations.RemoveField(
            model_name='propertyroom',
            name='room_number',
        ),
    ]
