from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from user.validator import Validator as validator



class MyUserManager(BaseUserManager):
    def create_superuser(self, email, password=None, **other_fields):

        other_fields.setdefault("is_active", True)
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **other_fields)

    def create_user(self, email=None, password=None, **other_fields):
        if not email:
            raise ValueError("Users must have an email address")

        if email:
            email = self.normalize_email(email)

        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(("first name"), max_length=50)
    last_name = models.CharField(max_length=50, default="", blank=True, null=True)
    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(
        max_length=14, validators=[validator.phone_number], unique=True, blank=True, null=True
    )
    picture = models.ImageField(
        default="image/profile/profile.*", upload_to="image/profile/"
    )
    address = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    last_seen = models.DateTimeField(_("Last Seen"), null=True, blank=True)
    objects = MyUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name

    def get_short_name(self):
        return "{}".format(self.first_name)

    def get_full_name(self):
        return "{} {}".format(self.first_name, self.last_name) if self.last_name else self.first_name



class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(_("email address"), blank=True, null=True)
    key = models.PositiveIntegerField(unique=True, null=True, blank=True)
    count = models.PositiveIntegerField(default=1)
    created = models.DateTimeField(auto_now=True)

    @property
    def expired(self):
        delta = self.created + timedelta(minutes=5) - now()
        return delta.total_seconds()

    @property
    def limit(self):
        delta = self.created + timedelta(minutes=10) - now()
        return int(delta.total_seconds())

    def __str__(self):
        return str(self.key) + " is sent to " + str(self.user)

