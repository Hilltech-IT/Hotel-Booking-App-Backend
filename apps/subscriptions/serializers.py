from rest_framework import serializers

from apps.subscriptions.models import Subscription, Pricing

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"



class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = "__all__"