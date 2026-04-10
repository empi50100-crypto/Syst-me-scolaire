"""Script pour corriger automatiquement les décorateurs @user_passes_test dans les fichiers de vues"""
import re
import os

# Chemins des fichiers à corriger
FILES_TO_FIX = {
    'finances/views.py': {
        'module': 'annee_scolaire',
        'pattern': r'@user_passes_test\(is_direction_or_comptable\)',
        'action_map': {
            'list': 'read',
            'detail': 'read',
            'create': 'write',
            'update': 'update',
            'edit': 'update',
            'delete': 'delete',
            'export': 'read',
            'stats': 'read',
            'statistics': 'read',
            'rapport': 'read',
            'report': 'read',
            'paiement': 'write',
            'salaire': 'write',
            'charge': 'write',
            'config': 'read',
            'compte': 'read',
            'personnel': 'write',
            'facture': 'write',
            'bourse': 'write',
            'eleve': 'read',
            'rappel': 'write',
            'cycle': 'write',
        }
    },
    'rapports/views.py': {
        'module': 'rapport_academique',
        'pattern': r'@user_passes_test\(is_direction_or_superadmin\)',
        'action_map': {
            'list': 'read',
            'detail': 'read',
            'create': 'write',
            'generate': 'read',
            'export': 'read',
            'bulletin': 'read',
            'rapport': 'read',
        }
    },
    'accounts/views.py': {
        'module': 'user_list',
        'pattern': r'@user_passes_test\(is_direction_or_superadmin\)',
        'action_map': {
            'list': 'read',
            'detail': 'read',
            'create': 'write',
            'update': 'update',
            'edit': 'update',
            'delete': 'delete',
            'permissions': 'update',
            'password': 'update',
            'toggle': 'update',
            'approve': 'update',
        }
    },
}

def get_action_from_function_name(func_name, action_map):
    """Déterminer l'action basée sur le nom de la fonction"""
    func_lower = func_name.lower()
    for key, action in action_map.items():
        if key in func_lower:
            return action
    return 'read'  # Par défaut

def fix_file(filepath, config):
    """Corriger les décorateurs dans un fichier"""
    print(f"\nTraitement de: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trouver toutes les fonctions avec le décorateur
    pattern = config['pattern']
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        print(f"  Aucun décorateur à corriger")
        return
    
    print(f"  {len(matches)} décorateur(s) à corriger")
    
    # Traiter chaque correspondance
    fixed_count = 0
    new_content = content
    
    # Chercher le motif de décorateur + fonction
    # @user_passes_test(...) \n @login_required \n def func_name
    decorator_pattern = r'(@user_passes_test\([^)]+\))\s*\n(@login_required\s*\n)(def \w+)\('
    
    for match in re.finditer(decorator_pattern, new_content):
        full_match = match.group(0)
        decorator = match.group(1)
        login_decorator = match.group(2)
        func_def = match.group(3)
        
        # Extraire le nom de la fonction
        func_name_match = re.search(r'def (\w+)', func_def)
        if func_name_match:
            func_name = func_name_match.group(1)
            action = get_action_from_function_name(func_name, config['action_map'])
            module = config['module']
            
            # Créer la nouvelle vérification
            check_code = f'''@login_required
def {func_name}(request):
    if not request.user.has_module_permission('{module}', '{action}'):
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette fonctionnalité.")
        return redirect('dashboard')
    '''
            
            new_content = new_content.replace(full_match, check_code, 1)
            fixed_count += 1
            print(f"  - {func_name} -> module='{module}', action='{action}'")
    
    if fixed_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  -> {fixed_count} décorateur(s) corrigé(s)")
    else:
        print(f"  -> Aucun changement effectué")

if __name__ == '__main__':
    base_path = r'C:\Users\empi5\Desktop\Système scolaire\gestion_ecole'
    
    print("="*60)
    print("CORRECTION DES DÉCORATEURS @user_passes_test")
    print("="*60)
    
    for filename, config in FILES_TO_FIX.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            fix_file(filepath, config)
        else:
            print(f"Fichier non trouvé: {filepath}")
    
    print("\n" + "="*60)
    print("CORRECTION TERMINÉE")
    print("="*60)
