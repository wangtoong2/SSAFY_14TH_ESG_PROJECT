from django.urls import path, include
from .views import GoogleLogin

urlpatterns = [
    # 로그인
    path('', include('dj_rest_auth.urls')),
    # 회원가입
    
    # 소셜 로그인
    path('google/', GoogleLogin.as_view(), name='google_login'),
    
]
