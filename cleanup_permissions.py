"""Script pour nettoyer les permissions qui bloquent l'accès"""
import os
import sys
import django

sys.path.insert(0, r'C:\Users\empi5\Desktop\Système scolaire\gestion_ecole')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Module, Permission, PermissionUtilisateur

def cleanup_blocking_permissions():
    print("="*60)
    print("NETTOYAGE DES PERMISSIONS BLOQUANTES")
    print("="*60)
    
    total_disabled = PermissionUtilisateur.objects.filter(est_actif=False).count()
    print(f"\nTotal permissions avec est_actif=False: {total_disabled}")
    
    print("\n--- Permissions désactivées par utilisateur ---")
    for pu in PermissionUtilisateur.objects.filter(est_actif=False).select_related('utilisateur', 'module'):
        print(f"  {pu.utilisateur.username} ({pu.utilisateur.role}): {pu.module.code} - actions={pu.actions}")
    
    print("\n" + "="*60)
    print("ACTION: Supprimer les PermissionUtilisateur avec est_actif=False")
    print("         Cela permettra aux permissions de RÔLE de s'appliquer")
    print("="*60)
    
    confirm = input("\nVoulez-vous supprimer ces permissions? (oui/non): ")
    
    if confirm.lower() in ['oui', 'yes', 'o', 'y']:
        deleted_count = PermissionUtilisateur.objects.filter(est_actif=False).delete()[0]
        print(f"\n{deleted_count} permissions supprimées!")
        print("Les permissions de RÔLE seront maintenant utilisées.")
    else:
        print("\nAucune modification effectuée.")
    
    print("\n--- Vérification après nettoyage ---")
    for user in User.objects.filter(role='professeur')[:3]:
        print(f"\n{user.username} ({user.role}):")
        for mod in Module.objects.filter(code__in=['fiche_notes', 'bulletins', 'presence_list']):
            result = user.has_module_permission(mod.code, 'read')
            print(f"  {mod.code}: {result}")

if __name__ == '__main__':
    cleanup_blocking_permissions()
