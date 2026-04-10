"""Script pour corriger automatiquement les décorateurs @user_passes_test"""
import re
import os

def fix_file(filepath):
    """Corriger les décorateurs dans un fichier"""
    print(f"\nTraitement de: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    fixed_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Chercher le motif: @login_required\n@user_passes_test(...)
        if '@login_required' in line and i + 1 < len(lines) and '@user_passes_test' in lines[i + 1]:
            # Garder @login_required et traiter le décorateur suivant
            new_lines.append(line)
            i += 1
            
            # Lire le décorateur @user_passes_test
            decorator_line = lines[i]
            
            # Déterminer le type de décorateur et l'action par défaut
            if 'is_direction_or_comptable' in decorator_line:
                module = 'annee_scolaire'
            elif 'is_direction_or_superadmin' in decorator_line:
                module = 'user_list'
            elif 'is_surveillance_or_direction_or_admin' in decorator_line:
                module = 'discipline'
            elif 'is_prof_or_surveillance_or_direction' in decorator_line:
                module = 'discipline'
            else:
                module = 'eleve_list'
            
            # Ajouter la vérification de permission
            new_lines.append(f'    if not request.user.has_module_permission("{module}", "read"):\n')
            new_lines.append(f'        messages.error(request, "Vous n\'avez pas l\'autorisation d\'accéder à cette fonctionnalité.")\n')
            new_lines.append(f'        return redirect(\'dashboard\')\n')
            
            fixed_count += 1
            print(f"  - Corrigé: {module}")
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    if fixed_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"  -> {fixed_count} décorateur(s) corrigé(s)")
    else:
        print(f"  -> Aucun décorateur @user_passes_test trouvé (après @login_required)")

if __name__ == '__main__':
    base_path = r'C:\Users\empi5\Desktop\Système scolaire\gestion_ecole'
    
    print("="*60)
    print("CORRECTION DES DÉCORATEURS @user_passes_test")
    print("="*60)
    
    files = [
        'finances/views.py',
        'rapports/views.py',
        'accounts/views.py',
    ]
    
    for filename in files:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            fix_file(filepath)
        else:
            print(f"Fichier non trouvé: {filepath}")
    
    print("\n" + "="*60)
    print("CORRECTION TERMINÉE")
    print("="*60)
