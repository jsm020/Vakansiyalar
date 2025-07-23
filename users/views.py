# Controller ball baholash endpointi
from users.models import IsController
from rest_framework.decorators import permission_classes

from .models import Diploma, Requirement, UserRequirement, UserRequirementScore
from .serializers import DiplomaSerializer, RequirementSerializer, SuperuserSerializer, UserRequirementSerializer
from .serializers import UserRequirementScoreSerializer
# UserRequirementScore API
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import get_object_or_404
from rest_framework.generics import get_object_or_404

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
from .models import Passport
from .serializers import PassportSerializer
from users.models import IsStaff, IsController, IsObserver, IsParticipant
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.serializers import MeSerializer
from rest_framework.decorators import api_view, permission_classes


@swagger_auto_schema(
    method='get',
    operation_summary="Foydalanuvchi uchun talablar ro'yxatini olish",
    operation_description="Tizimga kirgan foydalanuvchiga biriktirilgan talablar va ularning ma'lumotlarini qaytaradi.",
    responses={200: openapi.Response('Talablar ro‘yxati', examples={
        'application/json': {
            'user': 'username',
            'requirements': [
                {'id': 1, 'title': 'Talab 1', 'max_score': 10, 'controller': 'teacher1', 'created_at': '2025-07-18T12:00:00Z'}
            ]
        }
    })}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_requirements(request):
    user_requirements = UserRequirement.objects.filter(user=request.user).first()
    if not user_requirements:
        return Response({'error': 'Userga biriktirilgan talablar topilmadi.'}, status=404)
    talablar = user_requirements.requirements.all()
    result = []
    for req in talablar:
        result.append({
            'id': req.id,
            'title': req.title,
            'max_score': req.max_score,
            'controller': str(req.controller),
            'created_at': req.created_at,
        })
    return Response({'user': request.user.username, 'requirements': result})



score_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['user_id', 'requirement_id', 'score'],
    properties={
        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Baholanadigan foydalanuvchi IDsi'),
        'requirement_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Talab IDsi'),
        'score': openapi.Schema(type=openapi.TYPE_INTEGER, description='Beriladigan baho (ball)'),
    },
)

@swagger_auto_schema(
    method='post',
    request_body=score_request_schema,
    operation_summary="Talabga ball qo‘yish",
    operation_description="Controller roli ega foydalanuvchi boshqa foydalanuvchining talabini baholaydi.",
    responses={
        200: openapi.Response('Ball saqlandi', examples={
            'application/json': {'message': 'Ball saqlandi', 'score': 8}
        }),
        400: "Ma'lumotlar to'liq emas",
        404: "UserRequirement topilmadi"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsController])
def score_user_requirement(request):
    user_id = request.data.get('user_id')
    requirement_id = request.data.get('requirement_id')
    score = request.data.get('score')
    if not (user_id and requirement_id and score is not None):
        return Response({'error': 'user_id, requirement_id, score majburiy.'}, status=400)
    try:
        user_requirement = UserRequirement.objects.get(user_id=user_id, requirements__id=requirement_id)
    except UserRequirement.DoesNotExist:
        return Response({'error': 'UserRequirement topilmadi.'}, status=404)
    # Ballni saqlash
    from .models import UserRequirementScore
    urs, created = UserRequirementScore.objects.get_or_create(
        user_requirement=user_requirement,
        requirement_id=requirement_id,
        controller=request.user,
        defaults={'score': score}
    )
    if not created:
        urs.score = score
        urs.save()
    return Response({'message': 'Ball saqlandi', 'score': urs.score})


@swagger_auto_schema(tags=['Ruyxatdan utish'])
class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(description="User successfully registered"),
            400: openapi.Response(description="Validation error")
        },
        operation_description="Foydalanuvchini ro'yxatdan o'tkazadi"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(description="User successfully logged in"),
            401: openapi.Response(description="Invalid credentials"),
            400: openapi.Response(description="Validation error")
        },
        operation_description="Foydalanuvchini tizimga kirishini ta'minlaydi"
    )
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
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(description="Recovery token sent"),
            404: openapi.Response(description="User not found")
        },
        operation_description="Foydalanuvchining parolini tiklash"
    )
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
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="User information retrieved"),
            401: openapi.Response(description="Unauthorized")
        },
        operation_description="Foydalanuvchi ma'lumotlarini olish"
    )

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# Diplomas API
class DiplomaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsParticipant]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Diplomas retrieved successfully"),
            401: openapi.Response(description="Unauthorized")
        },
        operation_description="Foydalanuvchining diplomlarini olish"
    )

    def get(self, request):
        diplomas = Diploma.objects.filter(user=request.user)
        serializer = DiplomaSerializer(diplomas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DiplomaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class DiplomaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsParticipant]
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Diploma retrieved successfully"),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Diploma not found")
        },
        operation_description="Foydalanuvchining diplomini olish, yangilash yoki o'chirish"
    )

    def get_object(self, request, pk):
        return get_object_or_404(Diploma, pk=pk, user=request.user)

    def get(self, request, pk):
        diploma = self.get_object(request, pk)
        serializer = DiplomaSerializer(diploma)
        return Response(serializer.data)

    def put(self, request, pk):
        diploma = self.get_object(request, pk)
        serializer = DiplomaSerializer(diploma, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        diploma = self.get_object(request, pk)
        serializer = DiplomaSerializer(diploma, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        diploma = self.get_object(request, pk)
        diploma.delete()
        return Response(status=204)


# Passports API
class PassportListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsParticipant]
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Passports retrieved successfully"),
            401: openapi.Response(description="Unauthorized")
        },
        operation_description="Foydalanuvchining pasportlarini olish"
    )

    def get(self, request):
        passports = Passport.objects.filter(user=request.user)
        serializer = PassportSerializer(passports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PassportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class PassportDetailView(APIView):
    permission_classes = [IsAuthenticated, IsParticipant]
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Passport retrieved successfully"),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Passport not found")
        },
        operation_description="Foydalanuvchining pasportini olish, yangilash yoki o'chirish"
    )

    def get_object(self, request, pk):
        return get_object_or_404(Passport, pk=pk, user=request.user)

    def get(self, request, pk):
        passport = self.get_object(request, pk)
        serializer = PassportSerializer(passport)
        return Response(serializer.data)

    def put(self, request, pk):
        passport = self.get_object(request, pk)
        serializer = PassportSerializer(passport, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        passport = self.get_object(request, pk)
        serializer = PassportSerializer(passport, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        passport = self.get_object(request, pk)
        passport.delete()
        return Response(status=204)


# Requirements API
class RequirementListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStaff]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Requirements retrieved successfully"),
            401: openapi.Response(description="Unauthorized")
        },
        operation_description="Foydalanuvchining talablarini olish"
    )

    def get(self, request):
        requirements = Requirement.objects.all()
        serializer = RequirementSerializer(requirements, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Faqat superuser talab (requirement) controlleri bo‘la oladi.'}, status=403)
        serializer = RequirementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(controller=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



class RequirementDetailView(APIView):
    permission_classes = [IsAuthenticated, IsStaff]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Requirement retrieved successfully"),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Requirement not found")
        },
        operation_description="Talabni olish, yangilash yoki o'chirish"
    )

    def get_object(self, pk):
        return get_object_or_404(Requirement, pk=pk)

    def get(self, request, pk):
        requirement = self.get_object(pk)
        serializer = RequirementSerializer(requirement)
        return Response(serializer.data)

    def put(self, request, pk):
        requirement = self.get_object(pk)
        serializer = RequirementSerializer(requirement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        requirement = self.get_object(pk)
        serializer = RequirementSerializer(requirement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        requirement = self.get_object(pk)
        requirement.delete()
        return Response(status=204)

# UserRequirements API
class UserRequirementListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStaff]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="User requirements retrieved successfully"),
            401: openapi.Response(description="Unauthorized")
        },
        operation_description="Foydalanuvchining talablarini olish"
    )

    def get(self, request):
        user_requirements = UserRequirement.objects.filter(user=request.user)
        serializer = UserRequirementSerializer(user_requirements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserRequirementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class UserRequirementDetailView(APIView):
    permission_classes = [IsAuthenticated, IsStaff]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="User requirement retrieved successfully"),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="User requirement not found")
        },
        operation_description="Foydalanuvchining talabini olish, yangilash yoki o'chirish"
    )

    def get_object(self, pk):
        return get_object_or_404(UserRequirement, pk=pk, user=self.request.user)

    def get(self, request, pk):
        user_requirement = self.get_object(pk)
        serializer = UserRequirementSerializer(user_requirement)
        return Response(serializer.data)

    def put(self, request, pk):
        user_requirement = self.get_object(pk)
        serializer = UserRequirementSerializer(user_requirement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        user_requirement = self.get_object(pk)
        serializer = UserRequirementSerializer(user_requirement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user_requirement = self.get_object(pk)
        user_requirement.delete()
        return Response(status=204)
    
# Superuserlar ro‘yxati uchun API
class SuperuserListView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Superusers retrieved successfully"),
            401: openapi.Response(description="Unauthorized")
        },
        operation_description="Superuserlar ro'yxatini olish"
    )

    def get(self, request):
        superusers = User.objects.filter(is_superuser=True)
        serializer = SuperuserSerializer(superusers, many=True)
        return Response(serializer.data)
class UserRequirementScoreListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsController]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="User requirement scores retrieved successfully"),
            201: openapi.Response(description="User requirement score created successfully"),
            400: openapi.Response(description="Validation error")
        },
        operation_description="Foydalanuvchining talab ballarini olish yoki yaratish"
    )

    def get(self, request):
        scores = UserRequirementScore.objects.filter(user_requirement__user=request.user)
        serializer = UserRequirementScoreSerializer(scores, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserRequirementScoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class UserRequirementScoreDetailView(APIView):
    permission_classes = [IsAuthenticated, IsController]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="User requirement score retrieved successfully"),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="User requirement score not found")
        },
        operation_description="Foydalanuvchining talab ballarini olish, yangilash yoki o'chirish"
    )

    def get_object(self, pk):
        return get_object_or_404(UserRequirementScore, pk=pk, user_requirement__user=self.request.user)

    def get(self, request, pk):
        score = self.get_object(pk)
        serializer = UserRequirementScoreSerializer(score)
        return Response(serializer.data)

    def put(self, request, pk):
        score = self.get_object(pk)
        serializer = UserRequirementScoreSerializer(score, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        score = self.get_object(pk)
        serializer = UserRequirementScoreSerializer(score, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        score = self.get_object(pk)
        score.delete()
        return Response(status=204)

# Misol uchun, Requirement ro‘yxatini faqat kuzatuvchi ko‘ra olishi uchun:
from rest_framework.permissions import IsAuthenticated
from .models import IsObserver

class RequirementListView(APIView):
    permission_classes = [IsAuthenticated, IsObserver]
    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Requirements retrieved successfully"),
            401: openapi.Response(description="Unauthorized")
        },
        operation_description="Talablar ro'yxatini olish"
    )

    def get(self, request):
        requirements = Requirement.objects.all()
        serializer = RequirementSerializer(requirements, many=True)
        return Response(serializer.data)

from rest_framework.generics import ListAPIView
from .models import User
from .serializers import ControllerSerializer

class ControllerListView(ListAPIView):
    serializer_class = ControllerSerializer
    queryset = User.objects.filter(role='CONTROLLER')
    permission_classes = [IsAuthenticated, IsStaff]  # yoki kerakli permission