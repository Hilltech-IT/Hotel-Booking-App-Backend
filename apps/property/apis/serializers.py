from rest_framework import serializers

from apps.property.models import (Property, PropertyImage, PropertyRoom,
                                  PropertyRoomImage, ReviewAndRating)


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = "__all__"


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