from django.urls import path
from apps.property.apis.views import (
    PropertyAPIView, PropertyRetrieveUpdateDeleteAPIView, PropertyImageAPIView,
    PropertyRoomAPIView, PropertyRoomImageAPIView, PropertyRoomRetrieveUpdateDeleteAPIView,

)

urlpatterns = [
    path("", PropertyAPIView.as_view(), name="properties"),
    path("<int:pk>/", PropertyRetrieveUpdateDeleteAPIView.as_view(), name="properties"),
    path("rooms/", PropertyRoomAPIView.as_view(), name="rooms"),
    path("rooms/<int:pk>/", PropertyRoomRetrieveUpdateDeleteAPIView.as_view(), name="rooms"),
    path("property-images/", PropertyImageAPIView.as_view(), name="property-images"),
    path("room-images/", PropertyRoomImageAPIView.as_view(), name="room-images"),
]