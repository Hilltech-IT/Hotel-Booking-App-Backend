from django.urls import path

from apps.users.apis.views import (ChangePasswordAPIView,
                                   ForgotPasswordAPIView, RegisterUserAPIView,
                                   UserListAPIView, UserLoginAPIView,
                                   UserRetrieveUpdateDeleteAPIView)
from apps.users.views import (edit_staff, new_staff, onboard_service_provider,
                              staff, user_login, user_logout)

urlpatterns = [
    ## Main APP URLS
    path("staff/", staff, name="staff"),
    path("new-staff/", new_staff, name="new-staff"),
    path("edit-staff/", edit_staff, name="edit-staff"),

    # Service Providers
    path("onboarding/", onboard_service_provider, name="onboarding"),
    ## API URLS
    path("", UserListAPIView.as_view(), name="users"),
    path("<int:pk>/", UserRetrieveUpdateDeleteAPIView.as_view(), name="users"),
    path("register/", RegisterUserAPIView.as_view(), name="register"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot_password",),
    path("change-password/<str:token>/", ChangePasswordAPIView.as_view(), name="change_password",),
]