from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from apps.subscriptions.models import Pricing, Subscription
from apps.subscriptions.serializers import SubscriptionSerializer, PricingSerializer
from apps.users.models import User
from rest_framework import generics, status
from rest_framework.response import Response

date_today = datetime.now().date()
end_of_month = date_today + timedelta(days=30)
seven_days_from_today = date_today + timedelta(days=7)


# Create your views here.
class SubscriptionAPIView(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class SubscriptionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    lookup_field = "pk"


class PackagesAPIView(generics.ListCreateAPIView):
    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer


class PackagesDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer

    lookup_field = "pk"