from django.contrib import admin

from apps.bookings.models import RoomBooking


# Register your models here.
@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "room", "booked_from", "booked_to", "days_booked", "amount_paid"]