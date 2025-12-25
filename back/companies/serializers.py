from rest_framework import serializers

from .models import CorporateDisclosure
from .models import CompanyComment
from rest_framework import serializers


class CompanyCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = CompanyComment
        fields = (
            'id',
            'content',
            'user',
            'created_at',
            'updated_at',
            'likes_count',
            'is_liked',
            'liked',
        )

    def get_likes_count(self, obj):
        return obj.comment_likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            return obj.comment_likes.filter(user=request.user).exists()
        return False

    def get_liked(self, obj):
        return self.get_is_liked(obj)

    def get_user(self, obj):
        u = getattr(obj, 'user', None)
        if not u:
            return ''
        return getattr(u, 'nickname', None) or getattr(u, 'username', '')


class PreferencesSerializer(serializers.Serializer):
    desired_industries = serializers.ListField(child=serializers.CharField(), required=False)
    desired_size = serializers.ListField(child=serializers.CharField(), required=False)
    min_revenue = serializers.IntegerField(required=False)
    location = serializers.CharField(required=False)
    keywords = serializers.ListField(child=serializers.CharField(), required=False)
    min_growth = serializers.FloatField(required=False)
    weights = serializers.DictField(child=serializers.FloatField(), required=False)


class CorporateDisclosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateDisclosure
        fields = ['corp_name', 'disclosure_date', 'title', 'url']
