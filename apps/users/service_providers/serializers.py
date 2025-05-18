from apps.users.models import PropertyType, User
from rest_framework import serializers
from apps.users.serializers import UserBaseSerializer

class ServiceProviderSerializer(UserBaseSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    
class PropertyTypeUpdateSerializer(serializers.ModelSerializer):
    preferred_property_types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=PropertyType.objects.all()
    )

    class Meta:
        model = User
        fields = ['preferred_property_types']
        
class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = "__all__"