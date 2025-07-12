from django.urls import path

from apps.users.views import (
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    LoggedInUserProfileAPIView,
    RegisterUserAPIView,
    UserActivationAPIView,
    UserListAPIView,
    UserLoginAPIView,
    UserRetrieveUpdateDeleteAPIView,
    UserLogoutAPIView,
)


urlpatterns = [
    path("", UserListAPIView.as_view(), name="users"),
    path("<int:pk>/", UserRetrieveUpdateDeleteAPIView.as_view(), name="users"),
    path(
        "user-profile/",
        LoggedInUserProfileAPIView.as_view(),
        name="current-user-profile",
    ),
    path("register/", RegisterUserAPIView.as_view(), name="register"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path(
        "forgot-password/",
        ForgotPasswordAPIView.as_view(),
        name="forgot-password",
    ),
    path(
        "change-password/<str:token>/",
        ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
    path("activate-account/", UserActivationAPIView.as_view(), name="activate-account"),
]
