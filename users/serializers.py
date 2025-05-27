from rest_framework import serializers
from .models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_premium', 'data_saver')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data.get('first_name', 'Anonymous'),
            last_name=validated_data.get('last_name', 'User'),
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get("email_or_username")
        password = data.get("password")
        request = self.context.get('request')

        user = authenticate(
            request=request, username=identifier, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        token, _ = Token.objects.get_or_create(user=user)

        return {
            "token": token.key,
            "user": UserSerializer(user).data
        }
