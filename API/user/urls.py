from django.urls import path
from rest_framework.routers import DefaultRouter

from user import views

app_name = 'user'

router = DefaultRouter()
router.register("", views.UserViewSet, basename='user')

urlpatterns = [
    path('login/', views.LoginAuthToken.as_view(), name='login'),
    path('logout/', views.LogoutAuthToken.as_view(), name='logout'),
    path('user-retrieve/<pk>/', views.UserRetrieveAPI().as_view(), name='user-retrieve'),
]

urlpatterns += router.urls
