from apps.property.serializers import PropertyImageSerializer
from rest_framework import serializers

from apps.bookings.serializers import EventSpaceBookingSerializer
from apps.property.models import Property, PropertyRoom
from apps.property.serializers import PropertySerializer


class EventSapceRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyRoom
        fields = "__all__"


class EventSpaceSerializer(PropertySerializer):
    # eventspacebookings = EventSpaceBookingSerializer(many=True, read_only=True)
    # rooms = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    propertyimages = PropertyImageSerializer(many=True)

    class Meta:
        model = Property
        fields = "__all__"

    # def get_rooms(self, obj):
    #     rooms = obj.propertyrooms.select_related('property').prefetch_related('amenities')
    #     return EventSapceRoomSerializer(rooms, many=True).data

    def get_owner(self, obj):
        return {
            "id": obj.owner.id,
            "username": obj.owner.username,
            "first_name": obj.owner.first_name,
            "last_name": obj.owner.last_name,
            "email": obj.owner.email,
            "phone_number": obj.owner.phone_number,
            "country": obj.owner.country,
            "role": obj.owner.role,
        }


class EventSpaceCreateAndUpdateSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(
        max_length=255, allow_null=True, required=False
    )

    class Meta:
        model = Property
        fields = [
            "owner",
            "name",
            "location",
            "city",
            "country",
            "property_type",
            "address",
            "contact_number",
            "email",
            "cost",
            "capacity",
            "children_allowed",
            "adults_allowed",
            "profile_image",
            "amenities",
            "approval_status",
        ]
        extra_kwargs = {
            "amenities": {"required": False},
            "approval_status": {"required": False},
            "property_type": {"required": False},
        }
        partial = True
