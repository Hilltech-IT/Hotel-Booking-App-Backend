from apps.subscriptions.models import Subscription
from rest_framework import serializers
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.bookings.apis.serializers import (BnBBookingSerializer,
                                            EventSpaceBookingSerializer,
                                            RoomBookingSerializer)
from apps.core.validators import check_valid_password
from apps.events.apis.serializers import EventTicketSerializer
from apps.notifications.tasks import welcome_new_user_task
from apps.notifications.utils import reset_mail
from apps.users.models import User
from apps.users.utils import generate_unique_key

from apps.users.models import User

class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserListSerializer(UserBaseSerializer):
    hotel_bookings = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    tickets = serializers.SerializerMethodField()
    airbnb_bookings = serializers.SerializerMethodField()
    event_space_bookings = serializers.SerializerMethodField()


    def get_hotel_bookings(self, obj):
        data = obj.customerbookings.all()
        serializer = RoomBookingSerializer(instance=data, many=True)
        return serializer.data

    def get_payments(self, obj):
        return obj.customerpayments.values()

    
    def get_tickets(self, obj):
        data = obj.usereventtickets.all()
        serializer = EventTicketSerializer(instance=data, many=True)
        return serializer.data

    def get_airbnb_bookings(self, obj):
        data = obj.customerbnbbookings.all()
        serializer = BnBBookingSerializer(instance=data, many=True)
        return serializer.data

    def get_event_space_bookings(self, obj):
        data = obj.customereventspacebookings.all()
        serializer = EventSpaceBookingSerializer(instance=data, many=True)
        return serializer.data


class EditUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "id_number",
            "role",
            "phone_number",
            "gender",
            "address",
            "city",
            "country",

            
            "business_name",
            "business_address",
            "business_city",
            "business_country",
            "business_phone",
            "business_email",
            "business_number",
            
        ]
        read_only_fields = ["role"]
    # def validate(self, data):
    #     user = self.context["request"].user
    #     if user.role != "Service Provider":
    #         business_fields = [
    #             "business_name", "business_address", "business_city",
    #             "business_country", "business_phone", "business_email", "business_number"
    #         ]
    #         for field in business_fields:
    #             if field in data:
    #                 raise serializers.ValidationError(f"{field} is not allowed for your role.")
    #     return data

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "id_number",
            "role",
            "phone_number",
            "gender",
            "date_of_birth",
            "country",
            "address",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "country": {"required": False},
            "address": {"required": False},
            }

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
        # user.country = validated_data["country"]
        # user.address = validated_data["address"]
        user.date_of_birth = validated_data["date_of_birth"]
        user.gender = validated_data["gender"]
        user.save()

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
                "subject": "Welcome to Wonder Wise",
            }
            welcome_new_user_task(context_data=context_data, email=user.email)
        except Exception as e:
            raise e

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "preferred_property_types": list(user.preferred_property_types.values("id", "name")),
        }

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom data to the response
        # data['user'] = {
        #     'id': self.user.id,
        #     'username': self.user.username,
        #     'email': self.user.email,
        #     'first_name': self.user.first_name,
        #     'last_name': self.user.last_name,
        #     'role': self.user.role,
        # }
        user_data = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            "preferred_property_types": list(self.user.preferred_property_types.values("id", "name")),
        }
        # try:
        #     subscription = Subscription.objects.get(user=self.user)
        #     user_data['subscription'] = {
        #         'package': subscription.package.name if subscription.package else None,
        #         'status': subscription.status,
        #         'start_date': subscription.start_date,
        #         'end_date': subscription.end_date,
        #     }
        # except Subscription.DoesNotExist:
        #     user_data['subscription'] = None

        data['user'] = user_data
        
        return data


class ChangePasswordSerializer(serializers.Serializer):
    user = None
    password = serializers.CharField()
    repeat_password = serializers.CharField()

    def save(self, validated_data):
        token = self.context["token"]
        print(f"Token: {token}")
        print(f"Data: {validated_data}")

    
        self.user.set_password(validated_data["password"])
        self.user.token = None
        self.user.token_expiration_date = None
        if not self.user.is_active:
            self.user.activation_date = datetime.date.today()
        self.user.is_active = True
        self.user.save()

    def validate(self, data):
        self.check_valid_token()
        check_valid_password(data, user=self.user)

        return data

    def check_valid_token(self):
        try:
            self.user = User.objects.get(token=self.context["token"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Token is not valid.")
        fields = "__all__"


class UserActivationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500)


class ForgotPasswordSerializer(serializers.Serializer):
    user = None
    email = serializers.EmailField()

    def send_email(self):
        self.user.token = generate_unique_key(self.user.email)
        self.user.token_expiration_date = timezone.now() + timezone.timedelta(hours=24)
        self.user.IS_UPDATE = True
        self.user.save()
        reset_mail(self.user)

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with provided email!")
