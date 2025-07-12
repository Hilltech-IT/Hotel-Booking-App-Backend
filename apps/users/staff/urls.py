from django.urls import path

from apps.users.staff.views import StaffAPIView, StaffDetailAPIView

urlpatterns = [
    path("", StaffAPIView.as_view(), name="staff"),
    path("<int:pk>/", StaffDetailAPIView.as_view(), name="staff-details"),
]
