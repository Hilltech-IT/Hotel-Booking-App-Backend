# Generated by Django 4.2.7 on 2024-01-15 19:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('property', '0013_alter_property_property_type'),
        ('bookings', '0012_bnbbooking_notif_send_bnbbooking_payment_notif_send_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventSpaceBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('booked_from', models.DateField()),
                ('booked_to', models.DateField()),
                ('amount_expected', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=100)),
                ('days_booked', models.IntegerField(default=0)),
                ('fully_paid', models.BooleanField(default=False)),
                ('rooms_booked', models.IntegerField(default=1)),
                ('payment_link', models.URLField(null=True)),
                ('tx_ref', models.CharField(max_length=255, null=True)),
                ('transaction_id', models.CharField(max_length=255, null=True)),
                ('is_over', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('Pending Payment', 'Pending Payment'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('Paying', 'Paying')], default='Pending Payment', max_length=255, null=True)),
                ('payment_notif_send', models.BooleanField(default=False)),
                ('notif_send', models.BooleanField(default=False)),
                ('event_space', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='property.property')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customereventspacebookings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
