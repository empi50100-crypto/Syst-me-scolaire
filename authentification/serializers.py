from rest_framework import serializers
from authentification.models import User, Notification, Message, Service, Module, Permission


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    nom_complet = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 
                  'nom_complet', 'telephone', 'is_active', 'is_2fa_enabled', 'date_joined']
    
    def get_nom_complet(self, obj):
        return obj.get_full_name() or obj.username


class NotificationSerializer(serializers.ModelSerializer):
    type_notification_display = serializers.CharField(source='get_type_notification_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'destinataire', 'expediteur', 'titre', 'message', 'type_notification', 
                  'type_notification_display', 'est_lu', 'date_creation']


class MessageSerializer(serializers.ModelSerializer):
    expediteur_nom = serializers.CharField(source='expediteur.get_full_name', read_only=True)
    destinataire_nom = serializers.CharField(source='destinataire.get_full_name', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'expediteur', 'expediteur_nom', 'destinataire', 'destinataire_nom', 
                  'sujet', 'message', 'type_message', 'est_lu', 'date_envoi']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'nom', 'code', 'icon', 'ordre', 'est_actif']


class ModuleSerializer(serializers.ModelSerializer):
    service_nom = serializers.CharField(source='service.nom', read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'nom', 'code', 'url', 'icon', 'type_module', 'service', 'service_nom', 'ordre', 'est_actif']


class PermissionSerializer(serializers.ModelSerializer):
    module_nom = serializers.CharField(source='module.nom', read_only=True)
    
    class Meta:
        model = Permission
        fields = ['id', 'module', 'module_nom', 'role', 'actions']