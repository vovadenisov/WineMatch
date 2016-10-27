from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, AbstractUser, PermissionsMixin
from django.core.exceptions import PermissionDenied
from django.db import models

# Create your models here.
from django.utils import timezone
from survey.models import Wine, Favorites
#from favorites.models import Favorites

class UserModel(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(verbose_name="Email", blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    photo = models.CharField(default="", blank=True, null=True, max_length=255)
    get_notify = models.BooleanField(default=True, verbose_name=u"Получает оповещения")
    vk_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    faworits = models.ManyToManyField(Wine, through=Favorites, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def get_favorits(self):
        return self.favorites_set.all()

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return self.username

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        if self.is_active and self.is_superuser:
            return True

        for backend in auth.get_backends():
            if not hasattr(backend, 'has_module_perms'):
                continue
            try:
                if backend.has_module_perms(self, app_label):
                    return True
            except PermissionDenied:
                return False
        return False

