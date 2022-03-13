from django.urls import path
from rest_framework.routers import DefaultRouter

from post import views

app_name = 'post'

router = DefaultRouter()
router.register("like", views.LikeAPIView, basename='like')
router.register("", views.PostAPIView, basename='post')

urlpatterns = [
    path('all-list/', views.PostListAPIView.as_view(), name='all-post-list'),
    path('user/<int:id>/', views.UserPostListAPIView.as_view(), name='user-post-list'),
    path("detail/<int:id>/", views.PostDetail.as_view(), name="post-detail"),
    path("dislike/<int:id>/", views.DisLikeAPIView.as_view(), name="post-dislike"),
]

urlpatterns += router.urls
