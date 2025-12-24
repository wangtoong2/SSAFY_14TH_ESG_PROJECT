from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication


from django.shortcuts import get_object_or_404

from .serializers import ArticleListSerializer, ArticleSerializer, CommentSerializer
from .models import Article, ArticleLike, Comment, CommentLike


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def article_list(request):
    if request.method == 'GET':
        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def article_detail(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)

    # 🔐 작성자 체크 (GET 제외)
    if request.method in ['PUT', 'PATCH', 'DELETE']:
        if article.user != request.user:
            return Response(
                {'detail': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def article_like_toggle(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    user = request.user

    like, created = ArticleLike.objects.get_or_create(
        article=article,
        user=user
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return Response({
        'liked': liked,
        'likes_count': article.article_likes.count()
    })


# 댓글 관련    
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_list_create(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    # 댓글 목록
    if request.method == 'GET':
        comments = article.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    # 댓글 작성
    elif request.method == 'POST':
        print(request.data)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            article=article,
            user=request.user    # ✅ 이제 진짜 유저
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    if comment.user != request.user:
        return Response(status=403)

    comment.delete()
    return Response(status=204)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def comment_update(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    if comment.user != request.user:
        return Response({'detail': '권한 없음'}, status=403)

    serializer = CommentSerializer(
        comment,
        data=request.data,
        partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_like(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    like, created = CommentLike.objects.get_or_create(
        user=request.user,
        comment=comment
    )

    if not created:
        like.delete()
        return Response({'liked': False})

    return Response({'liked': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_like_toggle(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    user = request.user

    like, created = CommentLike.objects.get_or_create(
        comment=comment,
        user=user
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return Response({
        'liked': liked,
        'likes_count': comment.comment_likes.count()
    })

