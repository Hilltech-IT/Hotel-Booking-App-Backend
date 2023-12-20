from django.contrib import admin

from apps.property.models import PropertyRoom


# Register your models here.
@admin.register(PropertyRoom)
class PropertyRoomAdmin(admin.ModelAdmin):
    list_display = ["id", "property", "room_type", "rooms_number", "rooms_count", "booked", "rate"]