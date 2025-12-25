from rest_framework import serializers
from .models import Article, Comment, CommentLike


def _user_payload(u):
    if not u:
        return None
    avatar_url = None
    try:
        if getattr(u, 'avatar', None):
            avatar_url = u.avatar.url
    except Exception:
        avatar_url = None

    return {
        'username': getattr(u, 'username', '') or '',
        'nickname': getattr(u, 'nickname', '') or '',
        'avatar': avatar_url,
    }


class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    likes_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        # fields = ('id', 'title', 'content')
        fields = '__all__'

    def get_likes_count(self, obj):
        return obj.article_likes.count()

    def get_liked(self, obj):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            return obj.article_likes.filter(user=request.user).exists()
        return False
    
    def get_user(self, obj):
        u = getattr(obj, 'user', None)
        return _user_payload(u) or ''
    


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    likes_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('user', 'department_name', 'likes_count', 'liked')
        
    def get_likes_count(self, obj):
        return obj.article_likes.count()

    def get_liked(self, obj):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            return obj.article_likes.filter(user=request.user).exists()
        return False
    
    def get_user(self, obj):
        u = getattr(obj, 'user', None)
        return _user_payload(u) or ''

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

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
            'liked',
        )

    def get_likes_count(self, obj):
        return obj.comment_likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.comment_likes.filter(user=request.user).exists()
        return False

    def get_liked(self, obj):
        # Backward/forward compatibility: frontend may use either `liked` or `is_liked`.
        return self.get_is_liked(obj)

    def get_user(self, obj):
        u = getattr(obj, 'user', None)
        return _user_payload(u) or ''


class MyCommentSerializer(serializers.ModelSerializer):
    article_id = serializers.IntegerField(source='article.id', read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)
    department_name = serializers.CharField(source='article.department.name', read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'content',
            'created_at',
            'updated_at',
            'article_id',
            'article_title',
            'department_name',
        )




