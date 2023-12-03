from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.property.apis.views import (PropertyImageViewSet,
                                      PropertyModelViewSet,
                                      PropertyRoomImageViewSet,
                                      PropertyRoomViewSet,
                                      ReviewAndRatingViewSet)

router = DefaultRouter()
router.register("property-listings", PropertyModelViewSet, basename="property-listings")
router.register("property-images", PropertyImageViewSet, basename="property-images")
router.register("rooms", PropertyRoomViewSet, basename="rooms")
router.register("room-images", PropertyRoomImageViewSet, basename="room-images")
router.register("reviews-and-ratings", ReviewAndRatingViewSet, basename="reviews-and-ratings")


urlpatterns = [
    path("", include(router.urls)),
]