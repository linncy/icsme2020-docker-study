import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

try:
    User.objects.create_superuser('admin', 'webappadmin@dockerstudy.dev', 'password')
except Exception:
    print("Admin already exists!")