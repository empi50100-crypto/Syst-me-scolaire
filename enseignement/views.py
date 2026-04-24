from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import models
from django.db.models import Avg, Q, Count, Sum
from django.http import HttpResponse
from django.core.paginator import Paginator
from datetime import datetime, date
from enseignement.models import Classe, Matiere, Attribution, Evaluation, FicheNote, Salle, CoefficientMatiere, Examen, ContrainteHoraire, ProfilProfesseur
from enseignement.forms import ClasseForm, MatiereForm, AttributionForm, EvaluationForm, SalleForm, CoefficientMatiereForm, ExamenForm, ContrainteHoraireForm
from authentification.models import Utilisateur
from core.models import AnneeScolaire, PeriodeEvaluation


def is_direction_or_secretaire(user):
    return user.is_authenticated and (user.est_direction() or user.est_secretaire() or user.est_superadmin())


def is_direction_or_superadmin(user):
    return user.is_authenticated and (user.est_direction() or user.est_superadmin() or user.est_secretaire())


def is_professeur(user):
    return user.is_authenticated and hasattr(user, 'profil_professeur') and user.profil_professeur is not None


@login_required
def classe_list_view(request):
    if not request.user.has_module_permission('classe_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les classes.")
        return redirect('dashboard')
    
    annee_active = AnneeScolaire.objects.filter(est_active=True).first()
    classes_qs = Classe.objects.select_related('annee_scolaire').prefetch_related('inscriptions', 'matieres').order_by('niveau', 'nom', 'subdivision')
    
    # Get parameters
    search = request.GET.get('search', '')
    niveau_id = request.GET.get('niveau', '')
    annee_id = request.GET.get('annee', str(annee_active.id) if annee_active else '')
    subdivision = request.GET.get('subdivision', '')
    serie = request.GET.get('serie', '')
    
    if search:
        classes_qs = classes_qs.filter(Q(nom__icontains=search))
    if niveau_id:
        classes_qs = classes_qs.filter(niveau_id=niveau_id)
    if annee_id:
        classes_qs = classes_qs.filter(annee_scolaire_id=annee_id)
    if subdivision:
        classes_qs = classes_qs.filter(subdivision__icontains=subdivision)
    if serie:
        classes_qs = classes_qs.filter(serie__icontains=serie)
        
    annees = AnneeScolaire.objects.all().order_by('-date_debut')
    from core.models import NiveauScolaire
    niveaux = [(n.id, str(n)) for n in NiveauScolaire.objects.all()]
    series = []  # À remplir si nécessaire
    
    return render(request, 'enseignement/classe_list.html', {
        'classes': classes_qs,
        'search': search,
        'niveau_filter': niveau_id,
        'annee_filter': annee_id,
        'subdivision_filter': subdivision,
        'serie_filter': serie,
        'annees': annees,
        'niveaux': niveaux,
        'series': series,
    })


@login_required
def matiere_list_view(request):
    if not request.user.has_module_permission('matiere_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les matières.")
        return redirect('dashboard')
    
    matieres = Matiere.objects.prefetch_related('classes').all().order_by('nom')
    
    search = request.GET.get('search', '')
    if search:
        matieres = matieres.filter(nom__icontains=search)
    
    # Liste unique des matières existantes pour le datalist de recherche
    matieres_existantes = Matiere.objects.values_list('nom', flat=True).distinct().order_by('nom')
    
    return render(request, 'enseignement/matiere_list.html', {
        'matieres': matieres,
        'search': search,
        'matieres_existantes': matieres_existantes,
    })


@login_required
def professeur_list_view(request):
    if not request.user.has_module_permission('professeur_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les professeurs.")
        return redirect('dashboard')
    
    # Récupérer tous les utilisateurs avec le rôle professeur
    from authentification.models import Utilisateur
    professors = Utilisateur.objects.filter(role='professeur').prefetch_related('profil_professeur').order_by('last_name', 'first_name')
    
    search = request.GET.get('search', '')
    if search:
        professors = professors.filter(
            Q(last_name__icontains=search) | Q(first_name__icontains=search) | Q(username__icontains=search)
        )
    
    return render(request, 'enseignement/professeur_list.html', {
        'professeurs': professors,
        'search': search,
    })


@login_required
def classe_create_view(request):
    if not request.user.has_module_permission('classe_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de créer des classes.")
        return redirect('enseignement:classe_list')
    
    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classe créée avec succès.')
            return redirect('enseignement:classe_list')
    else:
        form = ClasseForm()
    return render(request, 'enseignement/classe_form.html', {'form': form})


@login_required
def classe_edit_view(request, pk):
    if not request.user.has_module_permission('classe_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des classes.")
        return redirect('enseignement:classe_list')
    
    classe = get_object_or_404(Classe, pk=pk)
    
    if request.method == 'POST':
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classe modifiée avec succès.')
            return redirect('enseignement:classe_list')
    else:
        form = ClasseForm(instance=classe)
    
    return render(request, 'enseignement/classe_form.html', {'form': form, 'classe': classe})


@login_required
def classe_delete_view(request, pk):
    if not request.user.has_module_permission('classe_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des classes.")
        return redirect('enseignement:classe_list')
    
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        classe.delete()
        messages.success(request, 'Classe supprimée avec succès.')
        return redirect('enseignement:classe_list')
    
    return render(request, 'enseignement/classe_confirm_delete.html', {'classe': classe})


@login_required
def matiere_create_view(request):
    if not request.user.has_module_permission('matiere_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des matières.")
        return redirect('enseignement:matiere_list')
    
    if request.method == 'POST':
        form = MatiereForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matière créée avec succès.')
            return redirect('enseignement:matiere_list')
    else:
        form = MatiereForm()
    matieres_existantes = Matiere.objects.values_list('nom', flat=True).distinct().order_by('nom')
    return render(request, 'enseignement/matiere_form.html', {'form': form, 'matieres_existantes': matieres_existantes, 'action': 'Ajouter'})


@login_required
def matiere_edit_view(request, pk):
    if not request.user.has_module_permission('matiere_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des matières.")
        return redirect('enseignement:matiere_list')
    
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        form = MatiereForm(request.POST, instance=matiere)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matière modifiée avec succès.')
            return redirect('enseignement:matiere_list')
    else:
        form = MatiereForm(instance=matiere)
    matieres_existantes = Matiere.objects.values_list('nom', flat=True).distinct().order_by('nom')
    return render(request, 'enseignement/matiere_form.html', {'form': form, 'matieres_existantes': matieres_existantes, 'action': 'Modifier'})


@login_required
def matiere_delete_view(request, pk):
    if not request.user.has_module_permission('matiere_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des matières.")
        return redirect('enseignement:matiere_list')
    
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        matiere.delete()
        messages.success(request, 'Matière supprimée avec succès.')
        return redirect('enseignement:matiere_list')
    return render(request, 'enseignement/matiere_confirm_delete.html', {'matiere': matiere})


@login_required
def salle_list_view(request):
    salles = Salle.objects.all().order_by('nom')
    search = request.GET.get('search', '')
    if search:
        salles = salles.filter(nom__icontains=search)
    return render(request, 'enseignement/salle_list.html', {'salles': salles})


@login_required
def professeur_create_view(request):
    if not request.user.est_direction() and not request.user.est_secretaire() and not request.user.est_admin():
        messages.error(request, "Vous n'avez pas la permission d'ajouter un professeur.")
        return redirect('enseignement:professeur_list')
    
    if request.method == 'POST':
        form_data = request.POST
        user_id = form_data.get('user')
        specialite_id = form_data.get('specialite')
        statut = form_data.get('statut', 'actif')
        
        try:
            user = Utilisateur.objects.get(pk=user_id)
            
            # Créer ou mettre à jour le profil professeur
            profil, created = ProfilProfesseur.objects.get_or_create(user=user)
            if specialite_id:
                profil.specialite_id = specialite_id
            profil.statut = statut
            profil.save()
            
            # Mettre à jour le rôle si nécessaire
            if not user.est_professeur():
                user.role = 'professeur'
                user.save()
            
            messages.success(request, f"Le professeur {user.get_full_name()} a été ajouté avec succès.")
            return redirect('enseignement:professeur_list')
        except Utilisateur.DoesNotExist:
            messages.error(request, "L'utilisateur sélectionné n'existe pas.")
    
    # Récupérer les utilisateurs qui ne sont pas déjà professeurs
    professeur_user_ids = ProfilProfesseur.objects.values_list('user_id', flat=True)
    users = Utilisateur.objects.filter(is_active=True).exclude(id__in=professeur_user_ids)
    
    # Filtrer pour n'afficher que les noms uniques de matières (sans doublons de coefficients)
    from django.db.models import Min
    ids_uniques = Matiere.objects.values('nom').annotate(id_min=Min('id')).values_list('id_min', flat=True)
    matieres = Matiere.objects.filter(id__in=ids_uniques).order_by('nom')
    
    return render(request, 'enseignement/professeur_form.html', {
        'users': users,
        'matieres': matieres,
        'is_direction_or_compta': request.user.est_direction() or request.user.est_comptable(),
        'is_secretaire': request.user.est_secretaire(),
        'is_direction': request.user.est_direction(),
    })


@login_required
def professeur_edit_view(request, pk):
    """Modifier un profil professeur existant"""
    if not request.user.has_module_permission('professeur_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier les professeurs.")
        return redirect('enseignement:professeur_list')
    
    profil = get_object_or_404(ProfilProfesseur, pk=pk)
    
    if request.method == 'POST':
        statut = request.POST.get('statut', profil.statut)
        matiere_id = request.POST.get('specialite')
        
        profil.statut = statut
        if matiere_id:
            profil.specialite_id = matiere_id
        profil.save()
        
        messages.success(request, f'Profil de {profil.user.get_full_name()} mis à jour.')
        return redirect('enseignement:professeur_list')
    
    # Pre-fill form with existing data
    # Date d'embauche : utiliser date_joined (création du compte) par défaut, format YYYY-MM-DD
    if profil.user.date_joined:
        date_embauche = profil.user.date_joined.strftime('%Y-%m-%d')
    else:
        date_embauche = ''
    
    form = {
        'nom': profil.user.last_name,
        'prenom': profil.user.first_name,
        'email': profil.user.email,
        'telephone': profil.user.telephone,
        'date_embauche': date_embauche,
        'statut': profil.statut,
        'salaire_base': '',
    }
    
    # Filtrer pour n'afficher que les noms uniques de matières (sans doublons de coefficients)
    from django.db.models import Min
    ids_uniques = Matiere.objects.values('nom').annotate(id_min=Min('id')).values_list('id_min', flat=True)
    matieres_list = Matiere.objects.filter(id__in=ids_uniques).order_by('nom')
    
    # Si le professeur a une matière qui n'est pas dans la liste filtrée, l'ajouter
    if profil.user.matiere_id and not matieres_list.filter(id=profil.user.matiere_id).exists():
        matiere_actuelle = Matiere.objects.filter(id=profil.user.matiere_id).first()
        if matiere_actuelle:
            matieres_list = list(matieres_list) + [matiere_actuelle]
    
    return render(request, 'enseignement/professeur_form.html', {
        'form': form,
        'profil': profil,
        'matieres': matieres_list,
        'selected_user': profil.user,
        'is_direction_or_compta': request.user.est_direction() or request.user.est_comptable(),
        'is_secretaire': request.user.est_secretaire(),
        'is_direction': request.user.est_direction(),
    })


@login_required
def professeur_delete_view(request, pk):
    """Supprimer un profil professeur"""
    if not request.user.has_module_permission('professeur_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer les professeurs.")
        return redirect('enseignement:professeur_list')
    
    profil = get_object_or_404(ProfilProfesseur, pk=pk)
    nom = profil.user.get_full_name()
    profil.delete()
    messages.success(request, f'Profil de {nom} supprimé.')
    return redirect('enseignement:professeur_list')


@login_required
def attribution_list_view(request):
    attributions = Attribution.objects.select_related('professeur__user', 'classe', 'matiere', 'annee_scolaire').all()
    return render(request, 'enseignement/attribution_list.html', {'attributions': attributions})


@login_required
def attribution_create_view(request):
    if not request.user.has_module_permission('attribution_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de créer des attributions.")
        return redirect('enseignement:attribution_list')
    
    if request.method == 'POST':
        form = AttributionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attribution créée avec succès.')
            return redirect('enseignement:attribution_list')
    else:
        form = AttributionForm()
    
    return render(request, 'enseignement/attribution_form.html', {'form': form})


@login_required
def mes_classes_view(request):
    profil_prof = getattr(request.user, 'profil_professeur', None)
    if not profil_prof:
        messages.error(request, "Vous n'êtes pas lié à un profil professeur.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    attributions = Attribution.objects.filter(
        professeur=profil_prof,
        annee_scolaire=annee
    ).select_related('classe', 'matiere', 'annee_scolaire')
    
    return render(request, 'enseignement/mes_classes.html', {'attributions': attributions})


@login_required
def saisie_notes(request):
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    if profil_prof:
        attributions = Attribution.objects.filter(professeur=profil_prof, annee_scolaire=annee)
        classes = Classe.objects.filter(attributions__in=attributions).distinct()
    else:
        classes = Classe.objects.filter(annee_scolaire=annee)
        
    return render(request, 'enseignement/saisie_notes.html', {'classes': classes})


@login_required
def saisie_notes_detail_view(request, classe_pk, matiere_pk):
    classe = get_object_or_404(Classe, pk=classe_pk)
    matiere = get_object_or_404(Matiere, pk=matiere_pk)
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    from scolarite.models import EleveInscription
    inscriptions = EleveInscription.objects.filter(classe=classe, annee_scolaire=annee).select_related('eleve')
    
    periodes = PeriodeEvaluation.objects.filter(annee_scolaire=annee)
    
    if request.method == 'POST':
        periode_id = request.POST.get('periode')
        type_eval = request.POST.get('type_eval')
        date_eval = request.POST.get('date_eval')
        
        for inscription in inscriptions:
            note = request.POST.get(f'note_{inscription.eleve.pk}')
            if note:
                Evaluation.objects.create(
                    eleve=inscription.eleve,
                    matiere=matiere,
                    classe=classe,
                    periode_id=periode_id,
                    annee_scolaire=classe.annee_scolaire,
                    type_eval=type_eval,
                    note=note,
                    date_eval=date_eval
                )
        messages.success(request, "Notes enregistrées avec succès.")
        return redirect('enseignement:mes_classes')
        
    return render(request, 'enseignement/saisie_notes.html', {
        'classe': classe,
        'matiere': matiere,
        'inscriptions': inscriptions,
        'periodes': periodes
    })


@login_required
def examen_list(request):
    if not request.user.has_module_permission('examen_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les examens.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    examens = Examen.objects.select_related('classe', 'matiere').filter(annee_scolaire=annee) if annee else Examen.objects.none()
    
    return render(request, 'enseignement/examen_list.html', {'examens': examens, 'annee': annee})


@login_required
def examen_create(request):
    messages.info(request, "La création d'examens sera bientôt disponible.")
    return redirect('enseignement:examen_list')


@login_required
def examen_detail(request, pk):
    messages.info(request, "La détail des examens sera bientôt disponible.")
    return redirect('enseignement:examen_list')


@login_required
def examen_edit(request, pk):
    messages.info(request, "La modification des examens sera bientôt disponible.")
    return redirect('enseignement:examen_list')


@login_required
def examen_delete(request, pk):
    messages.info(request, "La suppression des examens sera bientôt disponible.")
    return redirect('enseignement:examen_list')


@login_required
def contrainte_list(request):
    if not request.user.has_module_permission('contrainte_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les contraintes.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    contraintes = ContrainteHoraire.objects.select_related('classe', 'professeur').filter(annee_scolaire=annee) if annee else ContrainteHoraire.objects.none()
    
    return render(request, 'enseignement/contrainte_list.html', {'contraintes': contraintes, 'annee': annee})


@login_required
def contrainte_create(request):
    if not request.user.has_module_permission('contrainte_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de créer des contraintes.")
        return redirect('enseignement:contrainte_list')
    
    if request.method == 'POST':
        form = ContrainteHoraireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrainte horaire créée avec succès.')
            return redirect('enseignement:contrainte_list')
    else:
        form = ContrainteHoraireForm()
    
    return render(request, 'enseignement/contrainte_form.html', {'form': form, 'title': 'Nouvelle contrainte'})


@login_required
def contrainte_edit(request, pk):
    contrainte = get_object_or_404(ContrainteHoraire, pk=pk)
    
    if not request.user.has_module_permission('contrainte_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette contrainte.")
        return redirect('enseignement:contrainte_list')
    
    if request.method == 'POST':
        form = ContrainteHoraireForm(request.POST, instance=contrainte)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrainte horaire modifiée avec succès.')
            return redirect('enseignement:contrainte_list')
    else:
        form = ContrainteHoraireForm(instance=contrainte)
    
    return render(request, 'enseignement/contrainte_form.html', {'form': form, 'title': 'Modifier la contrainte', 'contrainte': contrainte})


@login_required
def contrainte_delete(request, pk):
    contrainte = get_object_or_404(ContrainteHoraire, pk=pk)
    
    if not request.user.has_module_permission('contrainte_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette contrainte.")
        return redirect('enseignement:contrainte_list')
    
    if request.method == 'POST':
        contrainte.delete()
        messages.success(request, 'Contrainte horaire supprimée avec succès.')
        return redirect('enseignement:contrainte_list')
    
    return render(request, 'enseignement/contrainte_delete.html', {'contrainte': contrainte})


@login_required
def emploi_du_temps(request):
    if not request.user.has_module_permission('emploi_du_temps', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les emplois du temps.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    classes = Classe.objects.filter(annee_scolaire=annee) if annee else []
    
    return render(request, 'enseignement/emploi_du_temps.html', {'classes': classes, 'annee': annee})


@login_required
def salle_create_view(request):
    if not request.user.has_module_permission('salle_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des salles.")
        return redirect('enseignement:salle_list')
    
    if request.method == 'POST':
        form = SalleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salle créée avec succès.')
            return redirect('enseignement:salle_list')
    else:
        form = SalleForm()
    
    return render(request, 'enseignement/salle_form.html', {'form': form, 'title': 'Nouvelle salle'})


@login_required
def salle_edit_view(request, pk):
    salle = get_object_or_404(Salle, pk=pk)
    
    if not request.user.has_module_permission('salle_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette salle.")
        return redirect('enseignement:salle_list')
    
    if request.method == 'POST':
        form = SalleForm(request.POST, instance=salle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salle modifiée avec succès.')
            return redirect('enseignement:salle_list')
    else:
        form = SalleForm(instance=salle)
    
    return render(request, 'enseignement/salle_form.html', {'form': form, 'title': 'Modifier la salle', 'salle': salle})


@login_required
def salle_delete_view(request, pk):
    salle = get_object_or_404(Salle, pk=pk)
    
    if not request.user.has_module_permission('salle_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette salle.")
        return redirect('enseignement:salle_list')
    
    if request.method == 'POST':
        salle.delete()
        messages.success(request, 'Salle supprimée avec succès.')
        return redirect('enseignement:salle_list')
    
    return render(request, 'enseignement/salle_delete.html', {'salle': salle})
