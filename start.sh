#!/bin/bash
set -e


# Django migration
python manage.py makemigrations
python manage.py migrate 

# Static fayllarni yig'ish
python manage.py collectstatic --noinput

# Superuser yaratish (agar mavjud bo'lmasa)
echo "from django.contrib.auth import get_user_model; User = get_user_model();\n" \
     "username = 'admin'; password = 'admin123';\n" \
     "email = 'admin@example.com';\n" \
     "User.objects.filter(username=username).exists() or User.objects.create_superuser(username=username, password=password, phone='+998000000000', first_name='Admin', last_name='Admin')" \
     | python manage.py shell

# Uvicorn serverini ishga tushurish
uvicorn vakansiyalar.asgi:application --host 0.0.0.0 --port 8000
