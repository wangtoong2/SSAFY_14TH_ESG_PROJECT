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
