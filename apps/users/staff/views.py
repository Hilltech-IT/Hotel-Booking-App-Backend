from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import redirect, render

from apps.notifications.tasks import welcome_new_user_task
from apps.users.tasks import account_activation_task
from apps.subscriptions.models import Pricing
from apps.users.models import User
from apps.users.utils import generate_unique_key

from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser

from apps.users.staff.serializers import StaffSerializer
from apps.core.constants import UserRoles



# Create your views here.
class StaffAPIView(generics.ListCreateAPIView):
    queryset = User.objects.filter(role=UserRoles.STAFF.value)
    serializer = StaffSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        data = request.data

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            try:
                user.role = UserRoles.STAFF.value
                token = generate_unique_key(user.email)
                user.token = token
                user.save()

                context_data = {
                    "name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "redirect_url": "{0}/activate-account/{1}".format(
                        settings.DEFAULT_FRONTEND_URL, user.token
                    ),
                    "subject": "Welcome to Wonder Wise",
                }
                welcome_new_user_task(context_data=context_data, email=user.email)
            except Exception as e:
                raise e
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = StaffSerializer

    lookup_field = "pk"
