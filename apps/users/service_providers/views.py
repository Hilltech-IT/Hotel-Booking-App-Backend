from django.conf import settings


from apps.notifications.tasks import welcome_new_user_task

from apps.users.models import User
from apps.users.utils import generate_unique_key

from rest_framework import status, generics
from apps.users.service_providers.serializers import ServiceProviderSerializer
from apps.core.constants import UserRoles


class ServiceProviderAPIView(generics.ListCreateAPIView):
    queryset = User.objects.filter(role=UserRoles.SERVICE_PROVIDER.value)
    serializer_class = ServiceProviderSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            user.role = UserRoles.SERVICE_PROVIDER.value
            token = generate_unique_key(user.email)
            user.token = token
            user.save()
            try:
                context_data = {
                    "name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "redirect_url": "{0}/activate-account/{1}".format(
                        settings.DEFAULT_FRONTEND_URL, user.token
                    ),
                    "subject": "Wonder Wise - Activate Account!",
                }
                welcome_new_user_task(context_data=context_data, email=user.email)
            except Exception as e:
                raise e
        return super().post(request, *args, **kwargs)


class ServiceProviderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(role=UserRoles.SERVICE_PROVIDER.value)
    serializer_class = ServiceProviderSerializer

    lookup_field = "pk"
