from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.bookings.apis.views import (
    AirBnBBookingDetailAPIView,
    AirBnBBookingsAPIView,
    BookAirBnBAPIView,
    BookARoomAPIView,
    BookAnAirBnBAPIView,
    BookAnEventSpaceAPIView,
    BookingFeeCalculationAPIView,
   
    CreateRoomBookingAPIView,
    DeleteRoomBookingAPIView,
    EventSpaceBookingDetailAPIView,
    EventSpaceBookingsModelViewSet,
    RevenueMetricsAPIView,
    RoomBookingAPIView,
    BookEventSpaceAPIView,
    RoomBookingsModelViewSet,
    UpdateAirbnbBookingAPIView,
    UpdateEventSpaceBookingAPIView,
    UpdateRoomBookingAPIView
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
router = DefaultRouter()
router.register(r'eventspace-bookings', EventSpaceBookingsModelViewSet, basename='eventspace-bookings')
router.register(r'room-bookings', RoomBookingsModelViewSet, basename='room-bookings')

urlpatterns = [
    
    path("bookings/", bookings, name="bookings"),
    path("reserve-room/", reserve_hotel_room, name="reserve-room"),


    #### API ENDPOINTS
    path('', include(router.urls)),
    path('metrics/revenue/', RevenueMetricsAPIView.as_view(), name='revenue-metrics'),

    path("customer-bookings/", RoomBookingAPIView.as_view(), name="customer-bookings"),
    path("book-a-room/", BookARoomAPIView.as_view(), name="book-a-room"),
    path("book-room/", CreateRoomBookingAPIView.as_view(), name="book-room"),
    path("update-room-booking/<int:pk>/", UpdateRoomBookingAPIView.as_view(), name="update-room-booking"),
    path("delete-room-booking/<int:pk>/", DeleteRoomBookingAPIView.as_view(), name="delete-room-booking"),
    path("airbnb-book/", BookAnAirBnBAPIView.as_view(), name="book-airbnb-new"),
    path("airbnb-book/<int:pk>/", UpdateAirbnbBookingAPIView.as_view(), name="update-aribnb-book-new"),
    path("event-space-book/", BookAnEventSpaceAPIView.as_view(), name="book-event-space-new"),
    path("event-space-book/<int:pk>/", UpdateEventSpaceBookingAPIView.as_view(), name="book-event-space-update-delete"),
    path("airbnb-booking-detail/<int:pk>/", AirBnBBookingDetailAPIView.as_view(), name="bnb-booking-details"),
    path("espace-booking-detail/<int:pk>/", EventSpaceBookingDetailAPIView.as_view(), name="espace-booking-details"),

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
    # path("airbnb-bookings/", airbnb_bookings, name="airbnb-bookings"),
    path("airbnb-bookings/", AirBnBBookingsAPIView.as_view(), name="airbnb-bookings"),
    path("book-airbnb/", book_airbnb, name="book-airbnb"),
    path("edit-airbnb-booking/", edit_airbnb_booking, name="edit-airbnb-booking"),
    path("book-an-airbnb/", BookAirBnBAPIView.as_view(), name="book-an-airbnb"),
    path("event-space-bookings/", event_space_bookings, name="event-space-bookings"),
    path("book-event-space/", book_event_space, name="book-event-space"),
    path("book-an-event-space/", BookEventSpaceAPIView.as_view(), name="book-an-event-space"),
]
