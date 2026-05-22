from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
class RoleEnum(models.TextChoices):
    EMPLOYE = "EMPLOYE", "Employé"
    RH      = "RH",      "Gestionnaire RH"
    ADMIN   = "ADMIN",   "Administrateur"

class UtilisateurManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Forcer ces champs pour le superuser
        extra_fields.setdefault('is_staff',     True)
        extra_fields.setdefault('is_active',    True)

        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractUser):
    username = None
    email    = models.EmailField(unique=True)
    role     = models.CharField(max_length=20,choices=RoleEnum.choices,blank=True,)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []   


    objects = UtilisateurManager()

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='%(class)s_set',
        related_query_name='%(class)s',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='%(class)s_set',
        related_query_name='%(class)s',
        verbose_name='user permissions',
    )

    class Meta:
        abstract = True

    def seConnecter(self):
        raise NotImplementedError(
            "La méthode seConnecter() doit être implémentée"
        )