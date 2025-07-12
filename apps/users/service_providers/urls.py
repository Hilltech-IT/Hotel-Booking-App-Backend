from django.urls import path

from apps.users.service_providers.views import (
    PropertyTypesAPIView,
    SelectPropertyTypeView,
    ServiceProviderAPIView,
    ServiceProviderDetailAPIView,
)

urlpatterns = [
    path("", ServiceProviderAPIView.as_view(), name="service-providers"),
    path(
        "<int:pk>/",
        ServiceProviderDetailAPIView.as_view(),
        name="service-provider-details",
    ),
    path(
        "select-property-type/",
        SelectPropertyTypeView.as_view(),
        name="select_property_type",
    ),
    path("property-types/", PropertyTypesAPIView.as_view(), name="property_types"),
]
