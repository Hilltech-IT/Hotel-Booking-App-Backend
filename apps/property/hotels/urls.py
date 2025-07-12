from django.urls import path
from apps.property.hotels.views import (
    ApproveHotelAPIView,
    CreateHotelRoomView,
    HotelAPIView,
    HotelCreateAPIView,
    HotelDetailAPIView,
    HotelRoomDetailView,
    HotelRoomListView,
    HotelUpdateAPIView,
    UpdateHotelRoomView,
)

urlpatterns = [
    path("", HotelAPIView.as_view(), name="hotels"),
    path("new/", HotelCreateAPIView.as_view(), name="create-hitel"),
    path("update/<int:pk>/", HotelUpdateAPIView.as_view(), name="update-hotel"),
    path("approve/<int:pk>/", ApproveHotelAPIView.as_view(), name="approve-hotel"),
    path("<int:pk>/", HotelDetailAPIView.as_view(), name="hotel-details"),
    # path("rooms/",HotelRoomListView.as_view(), name="hotel-rooms" ),
    # path('rooms/<int:pk>/', HotelRoomDetailView.as_view(), name='hotel-room-detail'),
    path("rooms/<int:pk>/", HotelRoomDetailView.as_view(), name="hotel-room-detail"),
    path("rooms/", HotelRoomListView.as_view(), name="hotel-rooms"),
    path("rooms/create/", CreateHotelRoomView.as_view(), name="hotel-rooms-create"),
    path(
        "rooms/update/<int:pk>/",
        UpdateHotelRoomView.as_view(),
        name="hotel-rooms-update",
    ),
]
