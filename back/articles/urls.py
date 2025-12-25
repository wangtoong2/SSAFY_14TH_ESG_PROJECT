from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.my_article_list),
    path('me/comments/', views.my_comment_list),
    path('user/<str:username>/', views.user_article_list),
    path('user/<str:username>/comments/', views.user_comment_list),
    path('', views.article_list),
    path('<int:article_pk>/', views.article_detail),
    path('<int:article_pk>/like/', views.article_like_toggle),

    path('<int:article_pk>/comments/', views.comment_list_create),
    path('comments/<int:comment_pk>/', views.comment_delete),
    path('comments/<int:comment_pk>/update/', views.comment_update),
    path('comments/<int:comment_pk>/like/', views.comment_like_toggle),
]

