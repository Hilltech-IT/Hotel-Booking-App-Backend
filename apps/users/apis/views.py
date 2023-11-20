from apps.users.models import User
from apps.users.apis.serializers import RegisterSerializer, UserListSerializer, UserLoginSerializer


from django.utils import timezone
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer


class UserLoginAPIView(ObtainAuthToken):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def get_serializer(self):
        return self.serializer_class()

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = Token.objects.get(user=user).key

        # Update last_login of the current user
        user.last_login = timezone.now()
        user.save()

        response = {
            'token': token,
            'pk': user.pk,
            'role': user.role,
            "username": user.username,
            "email": user.email,
            "name": f"{user.first_name} {user.last_name}"
            #'view_id': user.get_view_id,
        }

        return Response(response)

class RegisterUserAPIView(generics.CreateAPIView):

    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)