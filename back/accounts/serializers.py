from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    age = serializers.IntegerField()

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['age'] = self.validated_data.get('age')
        return data
    
    def save(self, request):
        user = super().save(request)
        user.age = self.validated_data.get('age')
        user.save()
        return user

class CustomUserDetailsSerializer(UserDetailsSerializer):
    email = serializers.EmailField(required=False)
    avatar = serializers.ImageField(read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + (
            'phone_number',
            'gender',
            'interests',
            'avatar',
        )
