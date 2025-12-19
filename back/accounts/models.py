from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    # 성별 옵션
    class GenderOptions(models.TextChoices):
        FEMALE = 'F', _('Female')
        MALE = 'M', _('Male')
        UNSPECIFIED = 'U', _('Unspecified')
    interests = models.TextField()  # 사용자의 관심사 (예: 'AI, Blockchain')
    skills = models.TextField()     # 사용자의 역량 (예: 'Python, Machine Learning')

    email = models.EmailField()
    # phonenumber = models.PhoneNumberField(_(""))
    birth = models.DateField()
    gender = models.CharField(
        max_length=1,
        choices=GenderOptions.choices,
        default=GenderOptions.UNSPECIFIED,
    )

    def __str__(self):
        return self.username