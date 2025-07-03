from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

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
    path('', include(router.urls)),
]
