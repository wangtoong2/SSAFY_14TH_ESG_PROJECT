from django.shortcuts import render

# Social login package
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

# Google login package
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter


# Create your views here.


class GoogleLogIn(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:8000/accounts/google/login/callback/'
    client_class = OAuth2Client


from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
<<<<<<< HEAD
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
=======
>>>>>>> f040f670656b0817c039ea6fe66b41c4dfe2c50e

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def withdraw_user(request):
    print("🔥 withdraw view called")
    print("🔥 user:", request.user)
    print("🔥 user id:", request.user.id)
    print("🔥 is authenticated:", request.user.is_authenticated)

    user = request.user

    if request.auth:
        request.auth.delete()

    user.delete()

    return Response(
        {'detail': '회원 탈퇴가 완료되었습니다.'},
        status=status.HTTP_200_OK
    )
<<<<<<< HEAD

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user

    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not user.check_password(old_password):
        return Response({'detail': '현재 비밀번호가 틀렸습니다.'}, status=400)

    validate_password(new_password, user)

    user.set_password(new_password)
    user.save()

    return Response({'detail': '비밀번호 변경 완료'})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def avatar_update(request):
    user = request.user
    avatar = request.FILES.get('avatar')

    if not avatar:
        return Response({'detail': 'No avatar'}, status=400)

    user.avatar = avatar
    user.save()

    return Response({
        'avatar': user.avatar.url
    })
=======
>>>>>>> f040f670656b0817c039ea6fe66b41c4dfe2c50e
