from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Member(models.Model):
    GENDERS = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('U', _('Unknown')),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=8, choices=GENDERS)
    birth_date = models.DateField(blank=True, null=True)