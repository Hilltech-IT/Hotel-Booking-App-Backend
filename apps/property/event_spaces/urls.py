from django.urls import path

from apps.property.event_spaces.views import (
    EventSpaceAPIView,
    EventSpaceCreateAPIVIew,
    EventSpaceDetailAPIView,
    EventSpaceUpdateAPIVIew,
)

urlpatterns = [
    path("", EventSpaceAPIView.as_view(), name="event-spaces"),
    path("<int:pk>/", EventSpaceDetailAPIView.as_view(), name="event-space-details"),
    path("new/", EventSpaceCreateAPIVIew.as_view(), name="create-espace"),
    path("update/<int:pk>/", EventSpaceUpdateAPIVIew.as_view(), name="update-espace"),
]
