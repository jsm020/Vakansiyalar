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
from users.serializers import MeSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]

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

    def get(self, request):
        superusers = User.objects.filter(is_superuser=True)
        serializer = SuperuserSerializer(superusers, many=True)
        return Response(serializer.data)
class UserRequirementScoreListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsController]

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

    def get(self, request):
        requirements = Requirement.objects.all()
        serializer = RequirementSerializer(requirements, many=True)
        return Response(serializer.data)