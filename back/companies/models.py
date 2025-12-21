from django.db import models

# Create your models here.
class Company(models.Model):
    """
    기업 정보를 저장하는 모델 (DART 기준)
    """
    corp_code = models.CharField(max_length=32, unique=True)  # DART에서 부여하는 고유 코드
    corp_name = models.CharField(max_length=255)
    stock_code = models.CharField(max_length=32, blank=True, null=True)  # 유가증권 코드(없을 수 있음)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return f"{self.corp_name} ({self.corp_code})"


class CorporateDisclosure(models.Model):
    """
    기업 공시 데이터를 저장하는 모델
    """
    corp_name = models.CharField(max_length=255)  # 기업명
    disclosure_date = models.DateField()          # 공시 날짜
    document_type = models.CharField(max_length=255)  # 문서 유형
    title = models.CharField(max_length=255)      # 공시 제목
    url = models.URLField()                       # 공시 문서 URL

    def __str__(self):
        return f"{self.corp_name} - {self.title}"