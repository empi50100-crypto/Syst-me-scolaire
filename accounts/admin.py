from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuditLog, RoleQuota, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations additionnelles', {'fields': ('role', 'telephone', 'eleve')}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model', 'object_repr', 'annee_scolaire', 'created_at']
    list_filter = ['action', 'model', 'created_at', 'annee_scolaire']
    search_fields = ['user__username', 'object_repr', 'details']
    readonly_fields = ['user', 'action', 'model', 'object_id', 'object_repr', 'details', 'ip_address', 'annee_scolaire', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 50
    
    fieldsets = (
        ('Informations', {
            'fields': ('user', 'action', 'model', 'object_repr')
        }),
        ('Détails', {
            'fields': ('object_id', 'details', 'ip_address', 'annee_scolaire', 'created_at')
        }),
    )


@admin.register(RoleQuota)
class RoleQuotaAdmin(admin.ModelAdmin):
    list_display = ['role', 'max_users', 'description']
    list_editable = ['max_users']
    search_fields = ['role']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['username', 'attempts', 'lock_count', 'locked_until', 'last_attempt', 'ip_address']
    list_filter = ['locked_until']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['username', 'attempts', 'lock_count', 'locked_until', 'last_attempt', 'ip_address', 'user_agent']
    date_hierarchy = 'last_attempt'
    ordering = ['-last_attempt']
    actions = ['unlock_accounts']
    
    fieldsets = (
        ('Informations', {
            'fields': ('username', 'attempts', 'lock_count', 'locked_until', 'last_attempt')
        }),
        ('Connexion', {
            'fields': ('ip_address', 'user_agent')
        }),
    )
    
    def unlock_accounts(self, request, queryset):
        from .models import LoginAttempt
        for attempt in queryset:
            LoginAttempt.unlock(attempt.username)
        self.message_user(request, f"{queryset.count()} compte(s) déverrouillé(s).")
    unlock_accounts.short_description = "Déverrouiller les comptes sélectionnés"
