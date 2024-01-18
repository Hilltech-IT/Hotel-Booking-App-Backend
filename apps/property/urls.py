from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.property.apis.views import (PropertyImageViewSet,
                                      PropertyModelViewSet,
                                      PropertyRoomImageViewSet,
                                      PropertyRoomViewSet,
                                      ReviewAndRatingViewSet)
from apps.property.views import (airbnb_details, bnb_properties, delete_room,
                                 edit_property, edit_room, event_space_details,
                                 event_spaces, new_property, new_room,
                                 properties, property_details)

router = DefaultRouter()
router.register("property-listings", PropertyModelViewSet, basename="property-listings")
router.register("property-images", PropertyImageViewSet, basename="property-images")
router.register("rooms", PropertyRoomViewSet, basename="rooms")
router.register("room-images", PropertyRoomImageViewSet, basename="room-images")
router.register(
    "reviews-and-ratings", ReviewAndRatingViewSet, basename="reviews-and-ratings"
)


urlpatterns = [
    path("api/", include(router.urls)),
    path("", properties, name="properties"),
    path("airbns/", bnb_properties, name="airbnbs"),
    path("airbnbs/<int:airbnb_id>/", airbnb_details, name="airbnb-details"),
    path("new-property/", new_property, name="new-property"),
    path("property/<int:property_id>/", property_details, name="property-details"),
    path("edit-property/", edit_property, name="edit-property"),
    ## Rooms
    path("new-room/", new_room, name="new-room"),
    path("edit-room/", edit_room, name="edit-room"),
    path("delete-room/", delete_room, name="delete-room"),

    path("event-spaces/", event_spaces, name="event-spaces"),
    path("event-spaces/<int:event_space_id>/", event_space_details, name="event-space-details"),
]
