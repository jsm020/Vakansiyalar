from rest_framework import serializers
from users.models import User

from drf_yasg.utils import swagger_serializer_method
from drf_yasg import openapi

class RegisterSerializer(serializers.ModelSerializer):
    """
    Foydalanuvchini ro'yxatdan o'tkazish uchun input maydonlari:
    - first_name: string
    - last_name: string
    - middle_name: string (ixtiyoriy)
    - phone: string (+998 bilan boshlanishi shart)
    - username: string
    - password: string
    """
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'middle_name', 'phone', 'username', 'password')
        extra_kwargs = {}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            middle_name=validated_data.get('middle_name'),
            phone=validated_data.get('phone'),
        )
        return user

class LoginSerializer(serializers.Serializer):
    """
    Login uchun input maydonlari:
    - username: string
    - password: string
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
