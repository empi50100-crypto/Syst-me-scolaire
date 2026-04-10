"""Supprimer les permissions bloquantes"""
import os
import sys
import django

sys.path.insert(0, r'C:\Users\empi5\Desktop\Système scolaire\gestion_ecole')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import PermissionUtilisateur, User, Module

print("="*60)
print("SUPPRESSION DES PERMISSIONS BLOQUANTES (est_actif=False)")
print("="*60)

deleted = PermissionUtilisateur.objects.filter(est_actif=False).delete()
print(f"\nPermissions supprimées: {deleted[0]}")

print("\n--- Vérification après suppression ---")
for user in User.objects.filter(role='professeur')[:3]:
    print(f"\n{user.username} ({user.role}):")
    for mod_code in ['fiche_notes', 'bulletins', 'presence_list', 'saisie_notes']:
        result = user.has_module_permission(mod_code, 'read')
        print(f"  {mod_code}: {result}")

print("\n" + "="*60)
print("Modules accessibles pour prof:")
print("="*60)
prof = User.objects.get(username='prof')
accessible = prof.get_accessible_modules()
print(f"Nombre: {accessible.count()}")
for m in accessible:
    print(f"  - {m.code}: {m.nom}")
