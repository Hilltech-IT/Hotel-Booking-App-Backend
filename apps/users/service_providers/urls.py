from django.urls import path

from apps.users.service_providers.views import (
    PropertyTypesAPIView,
    SelectPropertyTypeView,
    ServiceProviderAPIView,
    ServiceProviderActivationAPIView,
    ServiceProviderDetailAPIView,
    ServiceProviderListAPIView,
)

urlpatterns = [
    path("create/", ServiceProviderAPIView.as_view(), name="create-service-providers"),
    path("", ServiceProviderListAPIView.as_view(), name="service-providers"),
    path(
        "<int:pk>/",
        ServiceProviderDetailAPIView.as_view(),
        name="service-provider-details",
    ),
    path("<int:pk>/activate-toggle/", ServiceProviderActivationAPIView.as_view(), name="service-provider-activate-toggle"),
    path(
        "select-property-type/",
        SelectPropertyTypeView.as_view(),
        name="select_property_type",
    ),
    path("property-types/", PropertyTypesAPIView.as_view(), name="property_types"),
]
