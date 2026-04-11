from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import Utilisateur, Notification, Message, Service, Module, Permission, DemandeApprobation
from .serializers import (
    UserSerializer, NotificationSerializer, MessageSerializer,
    ServiceSerializer, ModuleSerializer, PermissionSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.Utilisateur.is_superadmin() or request.Utilisateur.is_direction()


class UserViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'is_active']
    
    def get_queryset(self):
        if self.request.Utilisateur.is_superadmin():
            return Utilisateur.objects.all()
        return Utilisateur.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.Utilisateur)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        Utilisateur = request.Utilisateur
        new_password = request.data.get('new_password')
        if new_password:
            Utilisateur.set_password(new_password)
            Utilisateur.save()
            return Response({'status': 'password changed'})
        return Response({'error': 'new_password required'}, status=400)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(destinataire=self.request.Utilisateur)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(est_lu=True)
        return Response({'status': 'all marked as read'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.est_lu = True
        notification.save()
        return Response({'status': 'marked as read'})


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        Utilisateur = self.request.Utilisateur
        return Message.objects.filter(
            models.Q(destinataire=Utilisateur) | models.Q(expediteur=Utilisateur)
        ).order_by('-date_envoi')
    
    @action(detail=False, methods=['get'])
    def inbox(self, request):
        messages = Message.objects.filter(destinataire=request.Utilisateur, est_lu=False)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        messages = Message.objects.filter(expediteur=request.Utilisateur)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(est_actif=True).order_by('ordre')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Module.objects.filter(est_actif=True).select_related('service').order_by('service__ordre', 'ordre')
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_service(self, request):
        service_code = request.query_params.get('service')
        modules = self.get_queryset()
        if service_code:
            modules = modules.filter(service__code=service_code)
        serializer = self.get_serializer(modules, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            Utilisateur = Utilisateur.objects.get(username=request.data.get('username'))
            response.data['Utilisateur'] = UserSerializer(Utilisateur).data
        return response
