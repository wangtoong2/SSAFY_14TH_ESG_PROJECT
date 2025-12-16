from django.urls import path, include
from .views import GoogleLogin

urlpatterns = [
    # 경로 이후 custom하기
    # 로그인
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # 회원가입
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # 소셜 로그인
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    
]
