from django.urls import path
from apps.property.hotels.views import HotelAPIView, HotelDetailAPIView

urlpatterns = [
    path("", HotelAPIView.as_view(), name="hotels"),
    path("<int:pk>/", HotelDetailAPIView.as_view(), name="hotel-details"),
]