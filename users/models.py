


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
    unique_number = models.PositiveIntegerField(unique=True, null=True, blank=True)

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

    def save(self, *args, **kwargs):
        import random
        from django.db import IntegrityError
        if self.unique_number is None:
            for _ in range(20):  # 20 marta urinish
                num = random.randint(10000, 99999)
                if not User.objects.filter(unique_number=num).exists():
                    self.unique_number = num
                    break
            if self.unique_number is None:
                raise IntegrityError("Yangi unique_number generatsiya qilib bo'lmadi. Iltimos, yana urining.")
        super().save(*args, **kwargs)

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


# Talab (Requriment) modeli
class Requirement(models.Model):
    title = models.CharField(max_length=255)
    max_score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    controller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requirements')  # Mas'ul superuser

    def __str__(self):
        return f"{self.title} (Mas'ul: {self.controller.username})"

# UserRequirement: Userga bir nechta talablar va har biriga score
class UserRequirement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_requirements')
    requirements = models.ManyToManyField(Requirement, related_name='user_requirements')
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def score(self):
        return sum(r.max_score for r in self.requirements.all())
    def __str__(self):
        return f"{self.user.username} - Talablar: {self.requirements.count()} - Score: {self.score}"


class UserRequirementScore(models.Model):
    user_requirement = models.ForeignKey(UserRequirement, on_delete=models.CASCADE, related_name='scores')
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    controller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_scores')  # Bahoni kim qo‘ydi
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.score > self.requirement.max_score:
            from django.core.exceptions import ValidationError
            raise ValidationError({'score': 'Score max_score dan oshmasligi kerak.'})

    def __str__(self):
        return f"{self.user_requirement.user.username} - {self.requirement.title}: {self.score}"