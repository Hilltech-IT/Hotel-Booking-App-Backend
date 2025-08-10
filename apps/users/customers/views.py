from apps.users.customers.filters import CustomerFilter
from apps.users.models import User
from apps.users.utils import generate_unique_key
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser

from apps.users.customers.serializers import CustomerSerializer
from apps.core.constants import UserRoles


class CustomersAPIView(generics.ListAPIView):
    queryset = User.objects.filter(role="customer")
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomerFilter
    pagination_class = None
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            customers = self.get_queryset()
            customers = self.filter_queryset(customers)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_customers = paginator.paginate_queryset(customers, request)
                serializer = self.get_serializer(paginated_customers, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(customers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
