# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)  # 사용자가 입력하는 필드

    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    # 관심사 N:M
    interests = models.ManyToManyField(Interest, related_name="users", blank=True)

    @property
    def age(self):
        """현재 나이 자동 계산"""
        if not self.birth_date:
            return None

        today = date.today()
        age = today.year - self.birth_date.year

        # 생일이 아직 안 지났으면 -1
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1

        return age

    def __str__(self):
        return self.username
