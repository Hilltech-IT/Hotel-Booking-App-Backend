from rest_framework import serializers

from apps.bookings.apis.serializers import BnBBookingSerializer
from apps.bookings.models import BnBBooking
from apps.property.apis.serializers import PropertyImageSerializer, PropertySerializer
from apps.property.models import Property
# from apps.property.serializers import PropertySerializer

class AirBnBSerializer(PropertySerializer):
    # bnbbookings = BnBBookingSerializer(many=True, read_only=True)
    propertyimages = PropertyImageSerializer(many=True)
    class Meta:
        model = Property
        fields = '__all__'
    

class AirBnBCreateSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(max_length=255, allow_null=True, required=False)

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
    
    