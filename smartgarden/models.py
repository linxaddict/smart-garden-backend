import datetime
from enum import Enum

import pytz
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

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
    username = models.TextField(verbose_name="user name", null=True, blank=True)
    user_type = models.CharField(choices=USER_TYPE_CHOICES, default='USER', null=False, max_length=255)

    objects = UserManager()

    @property
    def is_staff(self) -> bool:
        return bool(self.user_type == self.UserType.ADMIN.value) or self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_staff


class Circuit(models.Model):
    name = models.TextField(verbose_name='circuit name', null=False)
    active = models.BooleanField(verbose_name='active', null=False)
    health_check = models.DateTimeField(verbose_name='health check', null=True, blank=True)

    controller = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='controlled_circuit')
    collaborators = models.ManyToManyField(User, through='CircuitCollaboration',
                                           related_name='related_circuits', blank=True)

    @property
    def healthy(self):
        if self.health_check:
            # noinspection PyTypeChecker
            return (datetime.datetime.now(tz=pytz.UTC) - self.health_check).total_seconds() / 60 < 15
        else:
            return False

    @property
    def one_time_activation(self):
        if not self.one_time_activations:
            return None

        return self.one_time_activations \
            .filter(timestamp__date=datetime.date.today()) \
            .order_by('-timestamp') \
            .first()

    def __str__(self):
        return f'[{self.pk}] {self.name}'


class CircuitCollaboration(models.Model):
    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}, {self.circuit}'


class Activation(models.Model):
    amount = models.IntegerField(verbose_name='amount', null=False)
    timestamp = models.DateTimeField(verbose_name='timestamp', null=False)

    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE, related_name='activations')

    def __str__(self):
        return f'{self.circuit}, {self.timestamp}, {self.amount}'


class ScheduledOneTimeActivation(models.Model):
    amount = models.IntegerField(verbose_name='amount', null=False)
    timestamp = models.DateTimeField(verbose_name='timestamp', null=False)

    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE, related_name='one_time_activations')

    def __str__(self):
        return f'{self.circuit}, {self.timestamp}, {self.amount}'


class ScheduledActivation(models.Model):
    active = models.BooleanField(verbose_name='active', null=False)
    amount = models.IntegerField(verbose_name='amount', null=False)
    time = models.TimeField(verbose_name='activation time', null=False)
    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE, related_name='schedule')

    def __str__(self):
        return f'{self.circuit}, {self.time}, {self.amount}'
