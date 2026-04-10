"""Script pour reconstruire les fonctions manquantes dans accounts/views.py"""
import re

with open('accounts/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
i = 0

# Liste des fonctions attendues dans l'ordre
# On va détecter les motifs et reconstruire
pending_func_name = None
pending_decorators = []

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Si c'est un décorateur @login_required ou @user_passes_test
    if stripped in ['@login_required', '@user_passes_test']:
        pending_decorators.append(line)
        i += 1
        continue
    
    # Si on a des décorateurs en attente et la ligne suivante est du code
    if pending_decorators and stripped:
        # Chercher le type de code pour deviner le nom de la fonction
        if stripped.startswith('return render(request, \'accounts/'):
            # Extraire le nom du template
            match = re.search(r'\'accounts/(\w+)\.html\'', stripped)
            if match:
                func_name = match.group(1)
                if func_name in ['profile']:
                    pending_func_name = func_name
                elif func_name == 'user_list':
                    pending_func_name = 'user_list'
                elif func_name == 'user_form':
                    pending_func_name = 'user_create'
                elif func_name == 'user_confirm_delete':
                    pending_func_name = 'user_delete'
                else:
                    pending_func_name = func_name
            else:
                pending_func_name = 'view_func'
        elif stripped.startswith('return redirect(\'accounts:'):
            match = re.search(r'\'accounts:(\w+)\'', stripped)
            if match:
                pending_func_name = match.group(1)
            else:
                pending_func_name = 'redirect_view'
        elif stripped.startswith('if not request.user.has_module_permission'):
            # Chercher le module dans cette ligne
            match = re.search(r'has_module_permission\("(\w+)",\s*"(\w+)"\)', stripped)
            if match:
                module, action = match.groups()
                # Deviner le nom de la fonction basée sur le module
                if 'user_list' in module or 'user' in module:
                    pending_func_name = 'user_list'
                else:
                    pending_func_name = f'{module}_view'
            else:
                pending_func_name = 'permission_check_view'
        elif stripped.startswith('users = User.objects'):
            pending_func_name = 'user_list'
        elif stripped.startswith('user = get_object_or_404(User'):
            pending_func_name = 'user_detail'
        else:
            pending_func_name = 'view_func'
        
        # Ajouter les décorateurs
        for dec in pending_decorators:
            new_lines.append(dec)
        
        # Ajouter la définition de fonction
        if 'pk' in stripped or '(request, pk)' in stripped:
            new_lines.append(f'def {pending_func_name}(request, pk):')
        elif 'username' in stripped:
            new_lines.append(f'def {pending_func_name}(request, username):')
        elif 'user_id' in stripped:
            new_lines.append(f'def {pending_func_name}(request, user_id):')
        else:
            new_lines.append(f'def {pending_func_name}(request):')
        
        pending_decorators = []
        pending_func_name = None
        continue
    
    new_lines.append(line)
    i += 1

content_fixed = '\n'.join(new_lines)

with open('accounts/views.py', 'w', encoding='utf-8') as f:
    f.write(content_fixed)

print("Fichier accounts/views.py reconstruit")
