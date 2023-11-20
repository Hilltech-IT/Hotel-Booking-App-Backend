from django.urls import path

from apps.users.apis.views import (
    RegisterUserAPIView, UserListAPIView, UserLoginAPIView, UserRetrieveUpdateDeleteAPIView, 
    ForgotPasswordAPIView, ChangePasswordAPIView
)


urlpatterns = [
    path("", UserListAPIView.as_view(), name="users"),
    path("<int:pk>/", UserRetrieveUpdateDeleteAPIView.as_view(), name="users"),
    path("register/", RegisterUserAPIView.as_view(), name="register"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot_password",),
    path("change-password/<str:token>/", ChangePasswordAPIView.as_view(), name="change_password",),
]