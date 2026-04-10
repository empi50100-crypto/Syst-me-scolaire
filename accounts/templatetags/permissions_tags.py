from django import template

register = template.Library()

@register.filter
def has_module_permission(user, module_code):
    """Vérifie si l'utilisateur a la permission pour un module"""
    if not user.is_authenticated:
        return False
    return user.has_module_permission(module_code, 'read')

@register.simple_tag
def can_add(user, module_code):
    """Vérifie si l'utilisateur peut ajouter (write) dans un module"""
    if not user.is_authenticated:
        return False
    return user.has_module_permission(module_code, 'write')

@register.simple_tag
def can_change(user, module_code):
    """Vérifie si l'utilisateur peut modifier (update) dans un module"""
    if not user.is_authenticated:
        return False
    return user.has_module_permission(module_code, 'update')

@register.simple_tag
def can_delete(user, module_code):
    """Vérifie si l'utilisateur peut supprimer (delete) dans un module"""
    if not user.is_authenticated:
        return False
    return user.has_module_permission(module_code, 'delete')

@register.filter
def can_view(user, module_code):
    """Vérifie si l'utilisateur peut voir (read) dans un module"""
    if not user.is_authenticated:
        return False
    return user.has_module_permission(module_code, 'read')

@register.simple_tag
def get_user_services(user):
    """Retourne les services avec leurs modules pour l'utilisateur"""
    if not user.is_authenticated:
        return []
    return user.get_services_with_modules()

@register.filter
def get_module_url(module_code):
    """Retourne l'URL对应 à un code de module"""
    from accounts.models import Module
    module = Module.objects.filter(code=module_code).first()
    return module.url if module else '#'