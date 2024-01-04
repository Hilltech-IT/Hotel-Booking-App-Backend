from datetime import datetime

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import AuthenticationFailed

from apps.bookings.apis.serializers import RoomBookingSerializer
from apps.users.models import User
from apps.users.utils import generate_unique_key


class UserListSerializer(serializers.ModelSerializer):
    bookings = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "id_number", "role", "phone_number", "gender",
            "date_of_birth", "address", "country", "bookings", "payments"
        ]

    def get_bookings(self, obj):
        data = obj.customerbookings.all()
        serializer = RoomBookingSerializer(instance=data, many=True)
        return serializer.data

    def get_payments(self, obj):
        return obj.customerpayments.values()



class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "password", "first_name", "last_name", "id_number", "role",
            "phone_number", "gender", "date_of_birth", "country", "address")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"],
            validated_data["email"],
            validated_data["password"],   
        )
        user.first_name = validated_data["first_name"]
        user.last_name = validated_data["last_name"]
        user.id_number = validated_data["id_number"]
        user.role = validated_data["role"]
        user.phone_number = validated_data["phone_number"]
        user.country = validated_data["country"]
        user.address = validated_data["address"]
        user.date_of_birth = validated_data["date_of_birth"]
        user.gender = validated_data["gender"]
        user.save()

        return user


class UserLoginSerializer(AuthTokenSerializer):

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                # From Django 1.10 onwards the `authenticate` call simply
                # returns `None` for is_active=False users.
                # (Assuming the default `ModelBackend` authentication backend.)
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.', code='authorization')
            else:
                raise AuthenticationFailed('Unable to log in with provided credentials.', code='authorization')
        else:
            raise serializers.ValidationError('Must include "username" and "password".', code='authorization')

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    user = None
    password = serializers.CharField()
    repeat_password = serializers.CharField()

    def save(self, validated_data):
        self.user.set_password(validated_data["password"])
        self.user.token = None
        self.user.token_expiration_date = None
        if not self.user.is_active:
            self.user.activation_date = datetime.date.today()
        self.user.is_active = True
        self.user.save()

    def check_valid_token(self):
        try:
            self.user = User.objects.get(token=self.context["token"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Token is not valid.")
        fields = "__all__"


class ForgotPasswordSerializer(serializers.Serializer):
    user = None
    email = serializers.EmailField()

    
    def send_email(self):
        self.user.token = generate_unique_key(self.user.email)
        self.user.token_expiration_date = timezone.now() + timezone.timedelta(hours=24)
        self.user.save()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with provided email!")
    