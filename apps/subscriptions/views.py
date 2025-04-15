from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from apps.constants import IsAdminOrAuthenticated
from apps.subscriptions.models import Pricing, Subscription
from apps.subscriptions.serializers import CreateAndUpdateSubscriptionSerializer, SubscriptionSerializer, PricingSerializer
from apps.users.models import User
from rest_framework import generics, status
from rest_framework.response import Response

date_today = datetime.now().date()
end_of_month = date_today + timedelta(days=30)
seven_days_from_today = date_today + timedelta(days=7)


# Create your views here.
class SubscriptionAPIView(generics.ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminOrAuthenticated]
    def get_queryset(self):
        user = self.request.user
       
        if user.role == 'admin':
            subscriptions = self.queryset
        else:
            subscriptions = self.queryset.filter(user=user)

       

        return subscriptions
class CreateSubscriptionAPIView(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = CreateAndUpdateSubscriptionSerializer
    permission_classes = [IsAdminOrAuthenticated]
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class CancelSubscriptionAPIView(generics.UpdateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = CreateAndUpdateSubscriptionSerializer
    permission_classes = [IsAdminOrAuthenticated]
    lookup_field = 'pk' 

    def get_object(self):
        return Subscription.objects.get(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        subscription = self.get_object()
        subscription.status = "Cancelled"
        subscription.save()
        return Response({"message": "Subscription cancelled successfully."}, status=status.HTTP_200_OK)

class DeactivateSubscriptionAPIView(generics.UpdateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = CreateAndUpdateSubscriptionSerializer
    permission_classes = [IsAdminOrAuthenticated]
    lookup_field = 'pk' 
    def patch(self, request, *args, **kwargs):
        subscription = self.get_object()
        subscription.status = "Deactivated"
        subscription.save()
        return Response({"message": "Subscription deactivated by admin."}, status=status.HTTP_200_OK)
class ActivateSubscriptionAPIView(generics.UpdateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = CreateAndUpdateSubscriptionSerializer
    permission_classes = [IsAdminOrAuthenticated]
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        subscription = self.get_object()
        subscription.status = "Active"
        subscription.save()
        return Response({"message": "Subscription activated successfully."}, status=status.HTTP_200_OK)

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