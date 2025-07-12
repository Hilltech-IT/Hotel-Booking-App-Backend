from django.urls import path

from apps.subscriptions.views import (
    ActivateSubscriptionAPIView,
    CancelSubscriptionAPIView,
    CreateSubscriptionAPIView,
    DeactivateSubscriptionAPIView,
    SubscriptionAPIView,
    SubscriptionDetailAPIView,
    PackagesAPIView,
    PackagesDetailsAPIView,
)

urlpatterns = [
    # Subscriptions
    path("", SubscriptionAPIView.as_view(), name="subscriptions"),
    path("add/", CreateSubscriptionAPIView.as_view(), name="subscribe"),
    path("cancel/<int:pk>/", CancelSubscriptionAPIView.as_view(), name="cancel"),
    path(
        "deactivate/<int:pk>/",
        DeactivateSubscriptionAPIView.as_view(),
        name="deactivate",
    ),
    path("activate/<int:pk>/", ActivateSubscriptionAPIView.as_view(), name="activate"),
    path("<int:pk>/", SubscriptionDetailAPIView.as_view(), name="subscription-details"),
    # Packages
    path("packages/", PackagesAPIView.as_view(), name="packages"),
    path(
        "packages/<int:pk>/", PackagesDetailsAPIView.as_view(), name="package-details"
    ),
]
