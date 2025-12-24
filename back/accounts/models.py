from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    followings = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )

    phone_number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=(
            ('male', 'Male'),
            ('female', 'Female'),
        ),
        blank=True
    )
    interests = models.JSONField(default=list, blank=True)

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    nickname = models.CharField(max_length=150, blank=True)
    favorites = models.ManyToManyField(
        'companies.Company',
        related_name='favorited_by',
        blank=True,
    )
    
    def __str__(self):
        return self.username
