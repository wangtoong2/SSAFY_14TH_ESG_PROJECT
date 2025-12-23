from rest_framework import serializers
from .models import Article, Comment, CommentLike


class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        # fields = ('id', 'title', 'content')
        fields = '__all__'

    def get_likes_count(self, obj):
        return obj.article_likes.count()
    


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('user',)
        
    def get_likes_count(self, obj):
        return obj.article_likes.count()

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
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




