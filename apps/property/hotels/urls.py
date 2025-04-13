from django.urls import path
from apps.property.hotels.views import CreateHotelRoomView, HotelAPIView, HotelCreateAPIView, HotelDetailAPIView, HotelRoomListView,HotelUpdateAPIView, UpdateHotelRoomView

urlpatterns = [
    path("", HotelAPIView.as_view(), name="hotels"),
    path("new/", HotelCreateAPIView.as_view(), name="create-hitel"),
    path("update/<int:pk>/", HotelUpdateAPIView.as_view(), name="update-hotel"),
    path("<int:pk>/", HotelDetailAPIView.as_view(), name="hotel-details"),
    path("rooms/",HotelRoomListView.as_view(), name="hotel-rooms" ),
    path("rooms/create/",CreateHotelRoomView.as_view(),name="hotel-rooms-create" ),
    path("rooms/update/<int:pk>/",UpdateHotelRoomView.as_view(),name="hotel-rooms-update" ),
]