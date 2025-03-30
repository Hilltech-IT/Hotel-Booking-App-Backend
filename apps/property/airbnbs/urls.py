from django.urls import path
from apps.property.airbnbs.views import AirBnBAPIView, AirBnBDetailAPIView

urlpatterns = [
    path("", AirBnBAPIView.as_view(), name="airbnbs"),
    path("<int:pk>/", AirBnBDetailAPIView.as_view(), name="airbnb-details"),
]