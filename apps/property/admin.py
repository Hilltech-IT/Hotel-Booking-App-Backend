from django.contrib import admin

from apps.property.models import (
    Amenity,
    Property,
    PropertyImage,
    PropertyRoom,
    PropertyRoomImage,
)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
    ]


# Register your models here.
@admin.register(PropertyRoom)
class PropertyRoomAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "property",
        "room_type",
        "rooms_number",
        "rooms_count",
        "available_rooms",
        "booked",
        "rate",
    ]


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "owner",
        "property_type",
        "contact_number",
        "email",
        "cost",
        "property_address",
    ]


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "property",
        "image",
    ]


@admin.register(PropertyRoomImage)
class PropertyRoomImageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "room",
        "image",
    ]
