from rest_framework import serializers
from apps.users.serializers import UserBaseSerializer


class StaffSerializer(UserBaseSerializer):
    created_at = serializers.DateTimeField(read_only=True)
