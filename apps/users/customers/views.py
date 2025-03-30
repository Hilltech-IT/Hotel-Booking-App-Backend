from apps.users.models import User
from apps.users.utils import generate_unique_key

from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser

from apps.users.customers.serializers import CustomerSerializer
from apps.core.constants import UserRoles


class CustomersAPIView(generics.ListAPIView):
    queryset = User.objects.filter(role=UserRoles.CUSTOMER.value)
    serializer_class = CustomerSerializer

    