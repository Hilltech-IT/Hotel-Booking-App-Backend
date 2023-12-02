from apps.property.models import Property, PropertyImage, PropertyRoom, PropertyRoomImage
from rest_framework import serializers

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