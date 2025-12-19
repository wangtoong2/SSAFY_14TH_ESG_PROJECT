from django.db import models

# Create your models here.
class Company():
    pass


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