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
    path('', include(router.urls)),
    # Diplomas: fayl yuklash uchun media url misoli: /media/diplomas/filename.pdf
    path('diplomas/', views.DiplomaListCreateView.as_view(), name='diploma-list-create'),
    path('diplomas/<int:pk>/', views.DiplomaDetailView.as_view(), name='diploma-detail'),
]
