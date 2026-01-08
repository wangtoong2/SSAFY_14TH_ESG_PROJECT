from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article

# Article 모델의 post_save 신호를 이 함수가 받도록 설정
@receiver(post_save, sender=Article)
def article_post_save(sender, instance, created, **kwargs):
    # 'created'는 객체가 새로 생성되었을 때 True
    if created:
        print(f"알림: 새로운 게시글이 작성되었습니다! (제목: {instance.title})")