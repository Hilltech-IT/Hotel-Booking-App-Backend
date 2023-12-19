from django.urls import path
from apps.bookings.apis.views import BookARoomAPIView, RoomBookingAPIView

urlpatterns = [
    path("customer-bookings/", RoomBookingAPIView.as_view(), name="customer-bookings"),
    path("book-a-room/", BookARoomAPIView.as_view(), name="book-a-room"),
]