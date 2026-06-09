import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ton_projet.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@admin.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
nom = os.environ.get('DJANGO_SUPERUSER_NOM', 'Admin')
prenom = os.environ.get('DJANGO_SUPERUSER_PRENOM', 'Super')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        nom=nom,
        prenom=prenom
    )
    print(f"Superuser {email} créé.")
else:
    print(f"Superuser {email} existe déjà.")