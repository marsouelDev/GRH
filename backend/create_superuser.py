import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GRH.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'fmarsouel@gmail.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD','Max67172..')
nom = os.environ.get('DJANGO_SUPERUSER_NOM', 'Ngouadjio')
prenom = os.environ.get('DJANGO_SUPERUSER_PRENOM', 'Marsouel')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        nom=nom,
        prenom=prenom
    )
    print(f"Superuser {email} créé avec succès ")
else:
    print(f"Superuser {email} existe déjà ")