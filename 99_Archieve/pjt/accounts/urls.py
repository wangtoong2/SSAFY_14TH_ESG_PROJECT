from django.urls import path
from .views import (
    InterestListAPIView,
    UserListCreateAPIView,
    UserDetailAPIView,
)

urlpatterns = [
    path('interests/', InterestListAPIView.as_view()),
    path('users/', UserListCreateAPIView.as_view()),
    path('users/<int:pk>/', UserDetailAPIView.as_view()),
]
