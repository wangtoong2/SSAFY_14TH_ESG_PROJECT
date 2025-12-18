from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    # 성별 옵션
    class GenderOptions(models.TextChoices):
        FEMALE = 'F', _('Female')
        MALE = 'M', _('Male')
        UNSPECIFIED = 'U', _('Unspecified')
        
    # email = models.EmailField()
    # phonenumber = models.PhoneNumberField(_(""))
    # birth = models.DateField()
    # gender = models.CharField(
    #     max_length=1,
    #     choices=GenderOptions.choices,
    #     default=GenderOptions.UNSPECIFIED,
    # )
    pass
    