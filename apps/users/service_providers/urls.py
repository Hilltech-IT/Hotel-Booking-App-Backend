from django.urls import path

from apps.users.service_providers.views import ServiceProviderAPIView, ServiceProviderDetailAPIView

urlpatterns = [
    path("", ServiceProviderAPIView.as_view(), name="service-providers"),
    path("<int:pk>/", ServiceProviderDetailAPIView.as_view(), name="service-provider-details"),
]