from django.urls import path

from apps.bookings.apis.views import (BookARoomAPIView,
                                      BookingFeeCalculationAPIView,
                                      RoomBookingAPIView)
from apps.bookings.views import (airbnb_bookings, book_airbnb, bookings,
                                 make_booked_rooms_available,
                                 reserve_hotel_room)

urlpatterns = [
    path("", bookings, name="bookings"),
    path("reserve-room/", reserve_hotel_room, name="reserve-room"),
    #### API ENDPOINTS
    path("customer-bookings/", RoomBookingAPIView.as_view(), name="customer-bookings"),
    path("book-a-room/", BookARoomAPIView.as_view(), name="book-a-room"),
    path("calculate-booking-fee/", BookingFeeCalculationAPIView.as_view(), name="calculate-booking-fee"),
    path("make-rooms-available/", make_booked_rooms_available, name="make-rooms-available"),

    path("airbnb-bookings/", airbnb_bookings, name="airbnb-bookings"),
    path("book-airbnb/", book_airbnb, name="book-airbnb"),
]