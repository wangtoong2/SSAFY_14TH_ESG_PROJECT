from rest_framework import serializers
from .models import User, Interest

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    interests = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Interest.objects.all()
    )
    age = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'birth_date', 'gender', 'interests', 'age']

    def get_age(self, obj):
        return obj.age
