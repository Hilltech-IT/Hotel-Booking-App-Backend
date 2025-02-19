from django.urls import path

from apps.bookings.apis.views import (
    BookAirBnBAPIView,
    BookARoomAPIView,
    BookingFeeCalculationAPIView,
    RoomBookingAPIView,
    BookEventSpaceAPIView
)
from apps.bookings.views import (
    airbnb_bookings,
    book_airbnb,
    book_event_space,
    bookings,
    edit_airbnb_booking,
    event_space_bookings,
    make_booked_rooms_available,
    reserve_hotel_room,
)

urlpatterns = [
    path("", bookings, name="bookings"),
    path("reserve-room/", reserve_hotel_room, name="reserve-room"),
    #### API ENDPOINTS
    path("customer-bookings/", RoomBookingAPIView.as_view(), name="customer-bookings"),
    path("book-a-room/", BookARoomAPIView.as_view(), name="book-a-room"),
    path(
        "calculate-booking-fee/",
        BookingFeeCalculationAPIView.as_view(),
        name="calculate-booking-fee",
    ),
    path(
        "make-rooms-available/",
        make_booked_rooms_available,
        name="make-rooms-available",
    ),
    path("airbnb-bookings/", airbnb_bookings, name="airbnb-bookings"),
    path("book-airbnb/", book_airbnb, name="book-airbnb"),
    path("edit-airbnb-booking/", edit_airbnb_booking, name="edit-airbnb-booking"),
    path("book-an-airbnb/", BookAirBnBAPIView.as_view(), name="book-an-airbnb"),
    path("event-space-bookings/", event_space_bookings, name="event-space-bookings"),
    path("book-event-space/", book_event_space, name="book-event-space"),
    path("book-an-event-space/", BookEventSpaceAPIView.as_view(), name="book-an-event-space"),
]
