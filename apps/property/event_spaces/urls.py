from django.urls import path

from apps.property.event_spaces.views import EventSpaceAPIView, EventSpaceDetailAPIView

urlpatterns = [
    path("", EventSpaceAPIView.as_view(), name="event-spaces"),
    path("<int:id>/", EventSpaceDetailAPIView.as_view(), name="event-space-details"),
]