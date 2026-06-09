import os 
import django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GRH.settings') 
django.setup() 
from django.contrib.auth import get_user_model 
User = get_user_model() 
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin') 
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'nmarsouel@gmail.com') 
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD') 
if not User.objects.filter(username=username).exists(): 
    User.objects.create_superuser(username=username, email=email, password=password) 
    print("Superutilisateur cree avec succes") 
else: 
    print("Superutilisateur existe deja") 
