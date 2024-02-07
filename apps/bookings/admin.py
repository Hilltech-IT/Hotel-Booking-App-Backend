from django.contrib import admin

from apps.bookings.models import BnBBooking, RoomBooking, EventSpaceBooking


# Register your models here.
@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "room",
        "booked_from",
        "booked_to",
        "days_booked",
        "reference",
        "payment_link",
        "transaction_id",
        "amount_paid",
        "amount_expected",
        "notif_send",
    ]


@admin.register(BnBBooking)
class BnBBooking(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "airbnb",
        "booked_from",
        "booked_to",
        "amount_expected",
        "amount_paid",
        "payment_link",
        "amount_expected",
        "transaction_id",
        "reference",
        "notif_send",
    ]


@admin.register(EventSpaceBooking)
class EventSpaceBooking(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "event_space",
        "booked_from",
        "booked_to",
        "amount_expected",
        "amount_paid",
        "payment_link",
        "amount_expected",
        "transaction_id",
        "reference",
        "notif_send",
    ]