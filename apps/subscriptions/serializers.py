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
