from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(required=False, allow_blank=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['nickname'] = self.validated_data.get('nickname')
        return data
    
    def save(self, request):
        user = super().save(request)
        user.nickname = self.validated_data.get('nickname')
        user.save()
        return user

class CustomUserDetailsSerializer(UserDetailsSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    avatar = serializers.ImageField(read_only=True)

    nickname = serializers.CharField(required=False, allow_blank=True)
    is_social = serializers.SerializerMethodField()

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + (
            'phone_number',
            'gender',
            'interests',
            'avatar',
            'nickname',
            'is_social',
        )

    def get_is_social(self, obj):
        # django-allauth attaches SocialAccount via reverse relation.
        rel = getattr(obj, 'socialaccount_set', None)
        if rel is None:
            return False
        return rel.exists()
