import datetime
from enum import Enum

import pytz
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from smartgarden.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'

    class UserType(Enum):
        ADMIN = 'ADMIN'
        USER = 'USER'
        DEVICE = 'DEVICE'

    USER_TYPE_CHOICES = (
        (UserType.ADMIN.value, 'Admin'),
        (UserType.USER.value, 'User'),
        (UserType.DEVICE.value, 'Device')
    )

    email = models.EmailField(verbose_name='email address', unique=True)
    username = models.TextField(verbose_name="user name", null=True)
    user_type = models.CharField(choices=USER_TYPE_CHOICES, default='USER', null=False, max_length=255)

    objects = UserManager()

    @property
    def is_staff(self) -> bool:
        return bool(self.user_type == self.UserType.ADMIN.value) or self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_staff


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Circuit(models.Model):
    name = models.TextField(verbose_name='circuit name', null=False)
    active = models.BooleanField(verbose_name='active', null=False)
    health_check = models.DateTimeField(verbose_name='health check', null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='circuits')
    controller = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='controlled_circuit')

    @property
    def healthy(self):
        if self.health_check:
            # noinspection PyTypeChecker
            return (datetime.datetime.now(tz=pytz.UTC) - self.health_check).total_seconds() / 60 < 15
        else:
            return False


class Activation(models.Model):
    amount = models.IntegerField(verbose_name='amount', null=False)
    timestamp = models.DateTimeField(verbose_name='timestamp', null=False)

    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE, related_name='activations')


class ScheduledOneTimeActivation(models.Model):
    amount = models.IntegerField(verbose_name='amount', null=False)
    timestamp = models.DateTimeField(verbose_name='timestamp', null=False)

    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE, related_name='one_time_activations')


class ScheduledActivation(models.Model):
    active = models.BooleanField(verbose_name='active', null=False)
    amount = models.IntegerField(verbose_name='amount', null=False)
    time = models.TimeField(verbose_name='activation time', null=False)
    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE, related_name='schedule')
