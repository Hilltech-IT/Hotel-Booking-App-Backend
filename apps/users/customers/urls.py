from django.urls import path

from apps.users.customers.views import CustomersAPIView

urlpatterns = [
    path("", CustomersAPIView.as_view(), name="customers"),
]