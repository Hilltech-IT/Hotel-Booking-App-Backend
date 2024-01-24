from django.contrib import admin

from apps.property.models import Property, PropertyRoom


# Register your models here.
@admin.register(PropertyRoom)
class PropertyRoomAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "property",
        "room_type",
        "rooms_number",
        "rooms_count",
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
