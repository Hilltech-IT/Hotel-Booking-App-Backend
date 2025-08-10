from rest_framework import serializers
from django.db import transaction
from apps.bookings.serializers import RoomBookingSerializer
from apps.bookings.models import RoomBooking
from apps.property.serializers import (
    AmenitySerializer,
    PropertyImageSerializer,
    PropertyRoomImageSerializer,
    PropertyRoomSerializer,
    PropertySerializer,
)
from apps.property.models import Amenity, Property, PropertyImage, PropertyRoom, PropertyRoomImage

# from apps.property.serializers import PropertySerializer


class HotelRoomSerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True)
    property_name = serializers.CharField(source="property.name")
    roomimages = PropertyRoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = PropertyRoom
        fields = "__all__"


class CreateAndUpdateRoomSerializer(serializers.ModelSerializer):
    amenities = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(), many=True
    )
    profile_image = serializers.ImageField(
        max_length=255, allow_null=True, required=False
    )

    class Meta:
        model = PropertyRoom
        fields = [
            "property",
            "room_type",
            "rooms_number",
            "occupancy_capacity",
            "amenities",
            "view",
            "smoking_room",
            "accessibility_features",
            "rate",
            "check_in_time",
            "check_out_time",
            "available",
            "status",
            "charge_per_night",
            "rate",
            "booked_dates",
            "booked",
            "profile_image",
        ]
        extra_kwargs = {
            "amenities": {"required": False},
            "rate": {"required": False},
            "status": {"required": False},
            "booked": {"required": False},
            "booked_dates": {"required": False},
            "profile_image": {"required": False},
        }
    @transaction.atomic
    def create(self, validated_data):
        profile_image_file = validated_data.pop("profile_image", None)
        room_instance = super().create(validated_data)
        if profile_image_file:
            room_instance.profile_image = profile_image_file
            room_instance.save(update_fields=["profile_image"])
            PropertyRoomImage.objects.create(
                room=room_instance,
                image=profile_image_file
            )

        return room_instance
    
    @transaction.atomic
    def update(self, validated_data):
        profile_image_file = validated_data.pop("profile_image", None)
        room_instance = super().create(validated_data)
        if profile_image_file:
            room_instance.profile_image = profile_image_file
            room_instance.save(update_fields=["profile_image"])
            PropertyRoomImage.objects.create(
                room=room_instance,
                image=profile_image_file
            )

        return room_instance


class HotelCreateSerializer(serializers.ModelSerializer):
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
            "adults_allowed": {"required": False},
            "children_allowed": {"required": False},
            "capacity": {"required": False},
            "cost": {"required": False},
            "property_type": {"required": False},
            "approval_status": {"required": False},
        }
        partial = True
    @transaction.atomic
    def create(self, validated_data):
        profile_image_file = validated_data.pop("profile_image", None)
        property_instance = super().create(validated_data)
        if profile_image_file:
            property_instance.profile_image = profile_image_file
            property_instance.save(update_fields=["profile_image"])

            # Create the extra gallery/image record
            PropertyImage.objects.create(
                property=property_instance,
                image=profile_image_file
            )

        return property_instance
    @transaction.atomic
    def update(self, instance, validated_data):
        profile_image_file = validated_data.pop("profile_image", None)
        property_instance = super().update(instance, validated_data)
        
        if profile_image_file:
            property_instance.profile_image = profile_image_file
            property_instance.save(update_fields=["profile_image"])
            PropertyImage.objects.create(
                property=property_instance,
                image=profile_image_file
            )

        return property_instance

class HotelSerializer(PropertySerializer):
    rooms = serializers.SerializerMethodField()
    bookings = serializers.SerializerMethodField()
    propertyimages = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = "__all__"

    def get_propertyimages(self, obj):
        """Returns property images with full URLs."""
        return PropertyImageSerializer(
            obj.propertyimages.all(), 
            many=True, 
            context=self.context
        ).data

    def get_rooms(self, obj):
        """Returns the rooms with available_rooms added."""
        rooms = obj.propertyrooms.select_related("property").prefetch_related(
            "amenities"
        )
        # Serialize each room and include available_rooms
        rooms_data = PropertyRoomSerializer(
            rooms, 
            many=True, 
            context=self.context  # Pass context for nested  serializers
        ).data


        # Add available_rooms to each room
        for room, room_data in zip(rooms, rooms_data):
            room_data["available_rooms"] = room.available_rooms()

        return rooms_data

    def get_bookings(self, obj):
        rooms = obj.propertyrooms.all()
        bookings = RoomBooking.objects.filter(room__in=rooms)
        return RoomBookingSerializer(bookings, many=True).data
