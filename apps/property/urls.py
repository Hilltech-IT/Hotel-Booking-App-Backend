from django.urls import include, path
from apps.property.hotels.views import HotelRoomDetailView
from rest_framework.routers import DefaultRouter

from apps.property.apis.views import (AmenityViewSet, PropertyImageDeleteAPIView, PropertyImageUploadAPIView, PropertyImageViewSet,
                                      PropertyModelViewSet, PropertyRoomCreateAPIView, PropertyRoomImageDeleteAPIView, PropertyRoomImageUploadAPIView,
                                      PropertyRoomImageViewSet, PropertyRoomUpdateAPIView,
                                      PropertyRoomViewSet,
                                      ReviewAndRatingViewSet)


router = DefaultRouter()
router.register("property-listings", PropertyModelViewSet, basename="property-listings")
# router.register("property-images", PropertyImageViewSet, basename="property-images")
# router.register("rooms", PropertyRoomViewSet, basename="rooms")
# router.register("room-images", PropertyRoomImageViewSet, basename="room-images")
router.register(
    "reviews-and-ratings", ReviewAndRatingViewSet, basename="reviews-and-ratings"
)
router.register(
    "amenities", AmenityViewSet, basename="amenities"
)


urlpatterns = [
    path("api/", include(router.urls)),
    # new property images endpoints
    path("property-images/upload/<int:pk>/", PropertyImageUploadAPIView.as_view(), name="upload-property-images" ),
    path("property-images/<int:pk>/delete/", PropertyImageDeleteAPIView.as_view(), name="delete-property-images" ),
    path("room-images/upload/<int:pk>/", PropertyRoomImageUploadAPIView.as_view(), name="upload-room-images" ),
    path('property-room-images/<int:pk>/delete/', PropertyRoomImageDeleteAPIView.as_view(), name='delete-room-image'),
    path("rooms/create/", PropertyRoomCreateAPIView.as_view(), name="create-room" ),
    path("rooms/update/<int:pk>/", PropertyRoomUpdateAPIView.as_view(), name="create-room" ),
    # path("rooms/<int:pk>/", HotelRoomDetailView.as_view(), name="hotel-room-details" ),
    # path('hotels/rooms/<int:pk>/', HotelRoomDetailView.as_view(), name='hotel-room-detail'),

]
