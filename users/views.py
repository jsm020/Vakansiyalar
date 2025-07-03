from rest_framework.permissions import IsAuthenticated
from users.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from users.models import User
from django.conf import settings

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordRecoveryView(APIView):
    def post(self, request):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        token = PasswordResetTokenGenerator().make_token(user)
        # Bu yerda email orqali yuborish yoki boshqa usulni sozlash mumkin
        # Hozircha tokenni qaytaramiz (demo uchun)
        return Response({'recovery_token': token}, status=status.HTTP_200_OK)
# /me endpoint uchun view

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi

    @swagger_auto_schema(
        operation_description="Get current user info",
        responses={200: "User info"}
    )
    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "middle_name": user.middle_name,
            "phone": user.phone,
            "photo": user.main_photo.url if user.main_photo else None,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "date_joined": user.date_joined,
        }
        return Response(data)

    @swagger_auto_schema(
        operation_description="Update current user info (PUT)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Ism'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Familiya'),
                'middle_name': openapi.Schema(type=openapi.TYPE_STRING, description='Sharif'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Telefon'),
                'photo': openapi.Schema(type=openapi.TYPE_STRING, description='Rasm URL yoki fayl'),
            },
            required=['first_name', 'last_name', 'phone'],
        ),
        responses={200: "User info"}
    )
    def put(self, request):
        user = request.user
        fields = ["first_name", "last_name", "middle_name", "phone", "photo"]
        for field in fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return self.get(request)

    @swagger_auto_schema(
        operation_description="Partial update current user info (PATCH)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Ism'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Familiya'),
                'middle_name': openapi.Schema(type=openapi.TYPE_STRING, description='Sharif'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Telefon'),
                'photo': openapi.Schema(type=openapi.TYPE_STRING, description='Rasm URL yoki fayl'),
            },
        ),
        responses={200: "User info"}
    )
    def patch(self, request):
        return self.put(request)
    
