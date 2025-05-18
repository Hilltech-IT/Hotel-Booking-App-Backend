from django.conf import settings

from rest_framework.response import Response
from apps.notifications.tasks import welcome_new_user_task

from apps.users.models import PropertyType, User
from apps.users.utils import generate_unique_key

from rest_framework import status, generics
from apps.users.service_providers.serializers import  PropertyTypeSerializer, PropertyTypeUpdateSerializer, ServiceProviderSerializer
from apps.core.constants import UserRoles


class ServiceProviderAPIView(generics.ListCreateAPIView):
    queryset = User.objects.filter(role=UserRoles.SERVICE_PROVIDER.value)
    serializer_class = ServiceProviderSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username')
        if username and User.objects.filter(username=username).exists():
            return Response(
                {"error": "A user with that username already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = generate_unique_key(user.email)
            user.token = token
            print("user", user.role)
            user.role = "Service Provider"
            user.set_password(user.password)
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
                return Response(
                        {
                            "message": "Registration successful. Please check your email to activate your account.",
                            "email": user.email,
                            "activationToken": token,
                        },
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                raise e
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

class SelectPropertyTypeView(generics.UpdateAPIView):
    serializer_class = PropertyTypeUpdateSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
class PropertyTypesAPIView(generics.ListAPIView):
    queryset = PropertyType.objects.all() 
    serializer_class = PropertyTypeSerializer
    
    
class ServiceProviderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(role=UserRoles.SERVICE_PROVIDER.value)
    serializer_class = ServiceProviderSerializer

    lookup_field = "pk"
