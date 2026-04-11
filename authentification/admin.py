from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Utilisateur, JournalAudit, RoleQuota, TentativeConnexion, ProfilPermission, PermissionPersonnalisee


@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations additionnelles', {'fields': ('role', 'telephone', 'est_approuve')}),
    )


@admin.register(JournalAudit)
class JournalAuditAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'action', 'model', 'object_repr', 'annee_scolaire', 'created_at']
    list_filter = ['action', 'model', 'created_at', 'annee_scolaire']
    search_fields = ['utilisateur__username', 'object_repr', 'details']
    readonly_fields = ['utilisateur', 'action', 'model', 'object_id', 'object_repr', 'details', 'ip_address', 'annee_scolaire', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(RoleQuota)
class RoleQuotaAdmin(admin.ModelAdmin):
    list_display = ['role', 'max_users', 'description']
    list_editable = ['max_users']
    search_fields = ['role']


@admin.register(TentativeConnexion)
class TentativeConnexionAdmin(admin.ModelAdmin):
    list_display = ['username', 'attempts', 'lock_count', 'locked_until', 'ip_address']
    list_filter = ['locked_until']
    search_fields = ['username', 'ip_address']


@admin.register(ProfilPermission)
class ProfilPermissionAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description']


@admin.register(PermissionPersonnalisee)
class PermissionPersonnaliseeAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'module', 'niveau', 'est_actif']
