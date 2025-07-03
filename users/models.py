


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, first_name=None, last_name=None, middle_name=None, phone=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        if not phone:
            raise ValueError('Phone number is required')
        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, first_name=None, last_name=None, middle_name=None, phone=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, first_name, last_name, middle_name, phone, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=13, unique=True)

    def clean(self):
        super().clean()
        if self.phone and not self.phone.startswith('+998'):
            from django.core.exceptions import ValidationError
            raise ValidationError({'phone': 'Telefon raqam +998 bilan boshlanishi kerak.'})
    username = models.CharField(max_length=50, unique=True)

    main_photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    objects = UserManager()

    def __str__(self):
        return self.username

class Diploma(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='diplomas')
    specialization = models.CharField(max_length=100)
    graduation_year = models.CharField(max_length=4)
    diploma_number = models.CharField(max_length=20)
    diploma_file = models.FileField(upload_to='diplomas/')
    transcript_file = models.FileField(upload_to='transcripts/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.specialization} ({self.graduation_year})"



class Passport(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='passports')
    passport_seriya = models.CharField(max_length=2)
    passport_number = models.CharField(max_length=7)
    passport_jshir = models.CharField(max_length=14)
    cv_file = models.FileField(upload_to='cv_files/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.passport_seriya}{self.passport_number}"