from django.urls import path, include
from . import views

urlpatterns = [
    path('signup/', views.signup),
    path('login/', views.login),
    path('logout/', views.logout),
    path('delete/', views.delete),
    path('update/', views.update),
    path('profile/<username>/', views.profile),
    path('<int:user_pk>/follow/', views.follow),
]