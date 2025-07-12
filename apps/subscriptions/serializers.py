from rest_framework import serializers

from apps.subscriptions.models import Subscription, Pricing
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
        ]


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    package = PricingSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = "__all__"


class CreateAndUpdateSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )
    package = serializers.PrimaryKeyRelatedField(
        queryset=Pricing.objects.all(), required=True
    )
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Subscription
        fields = ["user", "package", "status", "start_date", "end_date"]
        extra_kwargs = {
            "status": {"default": "Active"},
            "start_date": {"required": False, "allow_null": True},
            "end_date": {"required": False, "allow_null": True},
        }
