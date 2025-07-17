from .models import Passport


from .models import Requirement, UserRequirement
from .models import Diploma
from rest_framework import serializers
from users.models import User
from .models import UserRequirementScore

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
    main_photo = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'middle_name', 'phone', 'username', 'password', 'main_photo')
        extra_kwargs = {}

    def create(self, validated_data):
        main_photo = validated_data.pop('main_photo', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            middle_name=validated_data.get('middle_name'),
            phone=validated_data.get('phone'),
        )
        if main_photo:
            user.main_photo = main_photo
            user.save()
        return user

class LoginSerializer(serializers.Serializer):
    """
    Login uchun input maydonlari:
    - username: string
    - password: string
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'middle_name',
            'phone',
            'main_photo',
            'is_active',
            'is_staff',
            'date_joined',
        ]
        read_only_fields = ['id', 'username', 'is_active', 'is_staff', 'date_joined']

    def update(self, instance, validated_data):
        main_photo = validated_data.get('main_photo', None)
        if main_photo and instance.main_photo:
            instance.main_photo.delete(save=False)  # eski faylni o‘chiradi
        return super().update(instance, validated_data)



class RequirementSerializer(serializers.ModelSerializer):
    controller = serializers.StringRelatedField()
    class Meta:
        model = Requirement
        fields = ["id", "title", "max_score", "controller", "created_at"]

class UserRequirementSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    requirements = RequirementSerializer(many=True, read_only=True)
    class Meta:
        model = UserRequirement
        fields = ["id", "user", "requirements", "score", "created_at"]

class DiplomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diploma
        fields = '__all__'
        read_only_fields = ['user']

class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = '__all__'
        read_only_fields = ['user']
       
        
##    
class SuperuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class UserRequirementScoreSerializer(serializers.ModelSerializer):
    user_requirement = serializers.StringRelatedField()
    requirement = serializers.StringRelatedField()
    controller = serializers.StringRelatedField()
    class Meta:
        model = UserRequirementScore
        fields = ["id", "user_requirement", "requirement", "score", "controller", "created_at"]

class ControllerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'phone', 'role']
