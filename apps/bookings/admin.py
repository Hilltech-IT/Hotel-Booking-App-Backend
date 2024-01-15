from django.contrib import admin

from apps.bookings.models import BnBBooking, RoomBooking


# Register your models here.
@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "room", "booked_from", "booked_to", "days_booked", "tx_ref", "transaction_id", "amount_paid", "notif_send"]


@admin.register(BnBBooking)
class BnBBooking(admin.ModelAdmin):
    list_display = ["id", "user", "airbnb", "booked_from", "booked_to", "amount_expected", "amount_paid", "transaction_id", "tx_ref", "notif_send"]
