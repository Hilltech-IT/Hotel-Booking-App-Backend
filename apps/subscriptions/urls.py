from django.urls import path

from apps.subscriptions.views import (
    SubscriptionAPIView, SubscriptionDetailAPIView,
    PackagesAPIView, PackagesDetailsAPIView
)

urlpatterns = [
    # Subscriptions
    path("", SubscriptionAPIView.as_view(), name="subscriptions"),
    path("<int:pk>/", SubscriptionDetailAPIView.as_view(), name="subscription-details"),
 
    # Packages
    path("packages/", PackagesAPIView.as_view(), name="packages"),
    path("<int:pk>/", PackagesDetailsAPIView.as_view(), name="package-details"),
]
