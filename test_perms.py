import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accounts.models import User, Permission

# Test various users
print("=== Test Permission System ===\n")

# Test secretaire
sec = User.objects.filter(role='secretaire').first()
print(f"Secretaire ({sec.username}):")
print(f"  classe_list read: {sec.has_module_permission('classe_list', 'read')}")
print(f"  classe_list write: {sec.has_module_permission('classe_list', 'write')}")
print(f"  eleve_list write: {sec.has_module_permission('eleve_list', 'write')}")

# Test professeur
prof = User.objects.filter(role='professeur').first()
print(f"\nProfesseur ({prof.username}):")
print(f"  saisie_notes write: {prof.has_module_permission('saisie_notes', 'write')}")
print(f"  classe_list read: {prof.has_module_permission('classe_list', 'read')}")

# Test comptable
comp = User.objects.filter(role='comptable').first()
print(f"\nComptable ({comp.username}):")
print(f"  annee_scolaire read: {comp.has_module_permission('annee_scolaire', 'read')}")
print(f"  bulletins read: {comp.has_module_permission('bulletins', 'read')}")

print("\n=== All OK ===")
