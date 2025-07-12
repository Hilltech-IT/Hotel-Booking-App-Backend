from django.urls import path
from apps.property.airbnbs.views import (
    AirBnBAPIView,
    AirBnBCreateAPIView,
    AirBnBDetailAPIView,
    AirBnBUpdateView,
)

urlpatterns = [
    path("", AirBnBAPIView.as_view(), name="airbnbs"),
    path("<int:pk>/", AirBnBDetailAPIView.as_view(), name="airbnb-details"),
    path("new/", AirBnBCreateAPIView.as_view(), name="create-hotel"),
    path("update/<int:pk>/", AirBnBUpdateView.as_view(), name="update-hotel"),
]
