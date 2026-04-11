from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import (
    UserViewSet, NotificationViewSet, MessageViewSet,
    ServiceViewSet, ModuleViewSet, PermissionViewSet, LoginView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='Utilisateur')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='api_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
