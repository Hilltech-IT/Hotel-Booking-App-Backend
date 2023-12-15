from rest_framework import serializers

from apps.property.models import (Property, PropertyImage, PropertyRoom,
                                  PropertyRoomImage, ReviewAndRating)


class PropertySerializer(serializers.ModelSerializer):
    single_rooms = serializers.SerializerMethodField()
    double_rooms = serializers.SerializerMethodField()
    suite_rooms = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = "__all__"

    def get_single_rooms(self, obj):
        return obj.propertyrooms.filter(room_type="Single").count()

    def get_double_rooms(self, obj):
        return obj.propertyrooms.filter(room_type="Double").count()

    def get_suite_rooms(self, obj):
        return obj.propertyrooms.filter(room_type="Suite").count()


class PropertyRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyRoom
        fields = "__all__"


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = "__all__"


class PropertyRoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyRoomImage
        fields = "__all__"


class ReviewAndRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewAndRating
        fields = "__all__"