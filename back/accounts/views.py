from django.shortcuts import render

# Social login
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

# OAuth2 providers (installed via django-allauth)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.models import SocialApp
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response
from rest_framework import status


class GoogleLogIn(SocialLoginView):
    """POST { access_token } -> returns DRF token key.

    Frontend SPA can use OAuth implicit flow and send the provider access_token.
    """

    adapter_class = GoogleOAuth2Adapter
    # If you later switch to authorization-code flow, set this to your SPA callback.
    callback_url = 'http://127.0.0.1:5173/login'
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except SocialApp.DoesNotExist:
            return Response(
                {
                    'detail': 'Google SocialApp이 설정되지 않았습니다. Django admin에서 SocialApp(Provider=Google)을 생성하고 Site에 연결하세요.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ImproperlyConfigured as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class KakaoLogIn(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    callback_url = 'http://127.0.0.1:5173/login'
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except SocialApp.DoesNotExist:
            return Response(
                {
                    'detail': 'Kakao SocialApp이 설정되지 않았습니다. Django admin에서 SocialApp(Provider=Kakao)을 생성하고 Site에 연결하세요.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ImproperlyConfigured as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class NaverLogIn(SocialLoginView):
    adapter_class = NaverOAuth2Adapter
    callback_url = 'http://127.0.0.1:5173/login'
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except SocialApp.DoesNotExist:
            return Response(
                {
                    'detail': 'Naver SocialApp이 설정되지 않았습니다. Django admin에서 SocialApp(Provider=Naver)을 생성하고 Site에 연결하세요.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ImproperlyConfigured as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

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

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user

    logger.debug('change_password called; user=%s, authenticated=%s', getattr(user, 'pk', None), user.is_authenticated if hasattr(user, 'is_authenticated') else None)
    logger.debug('request.data keys: %s', list(request.data.keys()))

    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({'detail': 'old_password and new_password are required.'}, status=400)

    if not user.check_password(old_password):
        return Response({'detail': '현재 비밀번호가 틀렸습니다.'}, status=400)

    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response({'detail': e.messages}, status=400)

    user.set_password(new_password)
    user.save()

    return Response({'detail': '비밀번호 변경 완료'}, status=200)

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
