from apps.users.models import User
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"



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