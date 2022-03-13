from http.client import NOT_FOUND
from django.db import IntegrityError
from rest_framework import generics, permissions, status, viewsets, views
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from post.models import Post, Like
from post.pagination import LargeResultPagination,\
     MediumResultPagination, SmallResultPagination
from post.serializers import *


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = MediumResultPagination
    queryset = Post.objects.all()


class UserPostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = LargeResultPagination
    queryset = None

    def get_queryset(self):
        user_id = self.kwargs.get('id')
        queryset = Post.objects.filter(owner_id=user_id)
        return queryset

class PostAPIView(ModelViewSet):
    queryset = None
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MediumResultPagination

    def get_queryset(self):
        return Post.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return PostSerializer
        elif self.action == "create":
            return PostCreateSerializer
        elif self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return PostCreateSerializer
        elif self.action == "my_post_likes":
            return LikeSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)

    @action(["get"], detail=False, url_path="my-post-likes")
    def my_post_likes(self, request, *args, **kwargs):
        queryset = Like.objects.filter(post__owner=request.user)
        serializer_class = self.get_serializer_class()
        page = self.paginator.paginate_queryset(queryset, self.request, view=self)
        if page is None: page = queryset
        serializer = serializer_class(page, many=True)
        data = serializer.data
        return self.get_paginated_response(data)


class LikeAPIView(ModelViewSet):
    queryset = None
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MediumResultPagination
    http_method_names = ['get', 'post', 'head']
    
    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return PostSerializer
        elif self.action == "create":
            return LikeCreateSerializer
        
    def list(self, serializer):
        queryset = [like.post for like in self.get_queryset()]
        page = self.paginator.paginate_queryset(queryset, self.request, view=self)
        if page is None: page = queryset
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(page, many=True)
        data = serializer.data
        return self.get_paginated_response(data)


    def perform_create(self, serializer):
        try:
            obj = serializer.save(user=self.request.user)
            post = obj.post
            if post.owner == self.request.user:
                raise NotFound("It is not allowed to like your own posts.")
            post.likes += 1
            post.save()
        except IntegrityError:
            raise NotFound("This post was already liked.")

    @action(["get"], detail=False, url_path="check-like")
    def check_like(self, request, *args, **kwargs):
        post_id = request.GET.get("id")
        if Like.objects.filter(post__owner=request.user, post_id=post_id).exists():
            return Response({"result": True}, status=status.HTTP_200_OK)
        return Response({"result": False}, status=status.HTTP_200_OK)

class DisLikeAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        error_msg = "You are not liked this post before."
        post_id = kwargs.get("id")
        try:
            like = Like.objects.get(post_id=post_id, user=request.user)
            post = like.post
            post.likes = max(post.likes - 1, 0)
            post.save()
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
        

class PostDetail(views.APIView):
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        error_msg = "Post with given id does not exist."
        post_id = kwargs.get("id")
        try:
            post = Post.objects.get(id=post_id)
        except (TypeError, ValueError, Post.DoesNotExist):
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
        
        if post.owner != request.user:
            post.views += 1
            post.save()
        serializer = self.serializer_class(post)
        data = serializer.data
        return Response(data)

