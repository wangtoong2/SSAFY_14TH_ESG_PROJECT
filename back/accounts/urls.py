from django.urls import path, include
from .views import GoogleLogIn
from . import views

urlpatterns = [
    # 로그인
    path('', include('dj_rest_auth.urls')),
    # 회원가입
    
    # 회원탈퇴
    path('delete/', views.delete),

    # 소셜 로그인
    path('google/', GoogleLogIn.as_view(), name='google_login'),
    

    # path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    # path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),

]
