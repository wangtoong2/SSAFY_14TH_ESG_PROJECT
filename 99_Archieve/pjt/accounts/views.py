from rest_framework import generics
from .models import User, Interest
from .serializers import UserSerializer, InterestSerializer


# ----------------------------
# Interest (관심사)
# ----------------------------

# 모든 관심사 조회
class InterestListAPIView(generics.ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer


# ----------------------------
# User (회원)
# ----------------------------

# GET: 사용자 목록 조회
# POST: 사용자 생성
class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# GET: 사용자 상세 조회
# PUT/PATCH: 사용자 수정
# DELETE: 사용자 삭제
class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
