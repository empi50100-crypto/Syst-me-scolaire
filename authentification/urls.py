from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password-recovery/', views.PasswordRecoveryView.as_view(), name='password_recovery'),
    path('password-recovery/verify/', views.PasswordRecoveryVerifyView.as_view(), name='password_recovery_verify'),
    path('password-recovery/reset/', views.PasswordRecoveryResetView.as_view(), name='password_recovery_reset'),
    path('profile/', views.profile, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('users/ajouter/', views.user_create, name='user_create'),
    path('users/<int:pk>/modifier/', views.user_update, name='user_update'),
    path('users/<int:pk>/supprimer/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/approuver/', views.user_approve, name='user_approve'),
    path('users/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:pk>/permissions/', views.user_permissions_detail, name='user_permissions_detail'),
    path('users/<int:pk>/reset-password/', views.user_reset_password, name='user_reset_password'),
    path('users/<int:user_pk>/permission/<str:module_code>/toggle/', views.user_permission_toggle, name='user_permission_toggle'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('messages/', views.message_list, name='message_list'),
    path('chat/', views.message_list, name='chat_inbox'),
    path('messages/nouveau/', views.message_create, name='message_create'),
]
