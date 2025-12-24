from rest_framework import serializers
from .models import Article, Comment, CommentLike


class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        # fields = ('id', 'title', 'content')
        fields = '__all__'

    def get_likes_count(self, obj):
        return obj.article_likes.count()
    
    def get_user(self, obj):
        u = getattr(obj, 'user', None)
        if not u:
            return ''
        return getattr(u, 'nickname', None) or getattr(u, 'username', '')
    


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('user',)
        
    def get_likes_count(self, obj):
        return obj.article_likes.count()
    
    def get_user(self, obj):
        u = getattr(obj, 'user', None)
        if not u:
            return ''
        return getattr(u, 'nickname', None) or getattr(u, 'username', '')

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'content',
            'user',
            'created_at',
            'updated_at',
            'likes_count',
            'is_liked',
        )

    def get_likes_count(self, obj):
        return obj.comment_likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.comment_likes.filter(user=request.user).exists()
        return False

    def get_user(self, obj):
        u = getattr(obj, 'user', None)
        if not u:
            return ''
        return getattr(u, 'nickname', None) or getattr(u, 'username', '')




