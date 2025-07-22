from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ControllerListView

router = DefaultRouter()
# Router faqat ViewSet lar uchun ishlaydi, APIView lar uchun path ishlatiladi

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('recovery/', views.PasswordRecoveryView.as_view(), name='password_recovery'),
    path('me/', views.MeView.as_view(), name='me'),
    path('me/photo/', views.MeView.as_view(), name='me-photo'),
    # Diplomas: fayl yuklash uchun media url misoli: /media/diplomas/filename.pdf
    path('diplomas/', views.DiplomaListCreateView.as_view(), name='diploma-list-create'),
    path('diplomas/<int:pk>/', views.DiplomaDetailView.as_view(), name='diploma-detail'),
    # Passports: fayl yuklash uchun media url misoli: /media/cv_files/filename.pdf
    path('passports/', views.PassportListCreateView.as_view(), name='passport-list-create'),
    path('passports/<int:pk>/', views.PassportDetailView.as_view(), name='passport-detail'),
    # Requirements
    path('requirements/', views.RequirementListCreateView.as_view(), name='requirement-list-create'),
    path('requirements/<int:pk>/', views.RequirementDetailView.as_view(), name='requirement-detail'),
    # UserRequirements
    path('user-requirements/', views.UserRequirementListCreateView.as_view(), name='user-requirement-list-create'),
    path('user-requirements/<int:pk>/', views.UserRequirementDetailView.as_view(), name='user-requirement-detail'),
    # UserRequirementScore
    path('user-requirement-scores/', views.UserRequirementScoreListCreateView.as_view(), name='user-requirement-score-list-create'),
    path('user-requirement-scores/<int:pk>/', views.UserRequirementScoreDetailView.as_view(), name='user-requirement-score-detail'),
    path('superusers/', views.SuperuserListView.as_view(), name='superuser-list'),
    path('controllers/', ControllerListView.as_view(), name='controller-list'),
    path('check-user-requirements/', views.check_user_requirements, name='check-user-requirements'),
    path('score-user-requirement/', views.score_user_requirement, name='score-user-requirement'),
    path('', include(router.urls)),
]
