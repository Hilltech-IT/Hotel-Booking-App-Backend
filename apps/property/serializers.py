from datetime import datetime, timedelta

from rest_framework import serializers

from apps.property.models import (
    Amenity,
    Property,
    PropertyImage,
    PropertyRoom,
    PropertyRoomImage,
    ReviewAndRating,
)
from apps.users.models import User

date_today = datetime.now().date()


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = "__all__"
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image and hasattr(instance.image, 'url'):
            if request:
                data['image'] = request.build_absolute_uri(instance.image.url)
            else:
                data['image'] = instance.image.url
        return data
    


class PropertyRoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyRoomImage
        fields = "__all__"
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image and hasattr(instance.image, 'url'):
            if request:
                data['image'] = request.build_absolute_uri(instance.image.url)
            else:
                data['image'] = instance.image.url
        return data
        
    



class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "business_name",
            "phone_number",
        ]


class PropertySerializer(serializers.ModelSerializer):
    single_rooms = serializers.SerializerMethodField()
    double_rooms = serializers.SerializerMethodField()
    suite_rooms = serializers.SerializerMethodField()
    # images = serializers.SerializerMethodField()
    booked_dates = serializers.ReadOnlyField(source="dates_booked")
    # profile_image = serializers.ImageField(required=False, allow_null=True)
    profile_image = serializers.SerializerMethodField() 
    amenities = AmenitySerializer(many=True, required=False)
    owner = OwnerSerializer(read_only=True)
    # amenities = serializers.PrimaryKeyRelatedField(
    #    queryset=Amenity.objects.all(),
    #    many=True,
    #    write_only=True,
    #    source="amenities"
    # )

    class Meta:
        model = Property
        fields = "__all__"
    def get_profile_image(self, obj):
        """Returns profile image with full URL."""
        request = self.context.get('request')
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            else:
                return obj.profile_image.url
        return None
    def get_single_rooms(self, obj):
        return obj.propertyrooms.filter(room_type="Single").count()

    def get_double_rooms(self, obj):
        return obj.propertyrooms.filter(room_type="Double").count()

    def get_suite_rooms(self, obj):
        return obj.propertyrooms.filter(room_type="Suite").count()

    # def get_images(self, obj):
    #     data = obj.propertyimages.all()
    #     serializer = PropertyImageSerializer(instance=data, many=True)
    #     return serializer.data

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     # print("Representation Data: ", representation)
    #     request = self.context.get("request")

    #     if request is not None:
    #         # Update image URLs to include the full URL
    #         images_data = representation.get("images", [])
    #         for image_data in images_data:
    #             image_data["image"] = request.build_absolute_uri(image_data["image"])

    #     return representation


class CreatePropertyRoomSerializer(serializers.ModelSerializer):
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
            "check_in_time",
            "check_out_time",
            "available",
            "status",
            "booked",
            "charge_per_night",
        ]

        extra_kwargs = {
            "amenities": {"required": False},
            "available": {"required": False},
            "status": {"required": False},
            "view": {"required": False},
            "booked": {"required": False},
            "check_in_time": {"required": False},
            "check_out_time": {"required": False},
            "occupancy_capacity": {"required": False},
        }
        partial = True


class PropertyRoomSerializer(serializers.ModelSerializer):
    rooms_count = serializers.SerializerMethodField()
    dates_booked = serializers.SerializerMethodField()
    property_name = serializers.CharField(source="property.name")
    available_rooms = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    class Meta:
        model = PropertyRoom
        fields = "__all__"
    def get_images(self, obj):
        # This ensures the context is passed to the nested serializer
        return PropertyRoomImageSerializer(
            obj.roomimages.all(), 
            many=True, 
            context=self.context
        ).data
    def get_rooms_count(self, obj):
        return obj.rooms_number - obj.booked

    def get_dates_booked(self, obj):
        bookings = obj.roombookings.filter(booked_to__gt=date_today)

        dates_list = []
        for booking in bookings:
            delta = booking.booked_to - booking.booked_from
            date_range = [
                booking.booked_from + timedelta(days=i) for i in range(delta.days + 1)
            ]
            dates_range_str = [date.strftime("%Y-%m-%d") for date in date_range]

            for x in dates_range_str:
                dates_list.append(x)

        return list(set(dates_list))
    

    def get_available_rooms(self, obj):
        """Expose available rooms in the API."""
        return obj.available_rooms()
    




class ReviewAndRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewAndRating
        fields = "__all__"
