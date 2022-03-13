from rest_framework import serializers 

from post.models import Post, Like
from user.serializers import UserSerializer

class PostSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    image = serializers.ImageField(required=False)
    class Meta:
        model = Post
        fields = ("id", "title", "description",  "image", "timestamp", "views", "likes", "owner")

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "description", "image")


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    class Meta:
        model = Like
        fields = "__all__"

class LikeCreateSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), source="post", write_only=True
    )
    class Meta:
        model = Like
        fields = ("post_id", "post")