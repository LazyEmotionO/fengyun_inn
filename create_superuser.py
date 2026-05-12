"""
快速建立 superuser 腳本
執行方式: python manage.py shell < create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fengyun_inn.settings')
django.setup()

from django.contrib.auth.models import User

username = 'cmlin'
password = '12345678'
email = 'cmlin@nfu.edu.tw'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser "{username}" created successfully!')
else:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'Superuser "{username}" password updated!')
