from django.urls import path

from apps.users.apis.views import RegisterUserAPIView, UserListAPIView, UserLoginAPIView


urlpatterns = [
    path("", UserListAPIView.as_view(), name="users"),
    path("register/", RegisterUserAPIView.as_view(), name="register"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
]