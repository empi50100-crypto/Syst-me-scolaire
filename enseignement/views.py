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
    niveaux = NiveauScolaire.objects.all()
    
    return render(request, 'enseignement/classe_list.html', {
        'classes': classes_qs,
        'search': search,
        'niveau_filter': niveau_id,
        'annee_filter': annee_id,
        'subdivision_filter': subdivision,
        'serie_filter': serie,
        'annees': annees,
        'niveaux': niveaux,
    })


@login_required
def matiere_list_view(request):
    if not request.user.has_module_permission('matiere_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les matières.")
        return redirect('dashboard')
    
    matieres = Matiere.objects.all().order_by('nom')
    
    search = request.GET.get('search', '')
    if search:
        matieres = matieres.filter(nom__icontains=search)
    
    return render(request, 'enseignement/matiere_list.html', {
        'matieres': matieres,
        'search': search,
    })


@login_required
def professeur_list_view(request):
    if not request.user.has_module_permission('professeur_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les professeurs.")
        return redirect('dashboard')
    
    professors = ProfilProfesseur.objects.select_related('user').order_by('user__last_name', 'user__first_name')
    
    search = request.GET.get('search', '')
    if search:
        professors = professors.filter(
            Q(user__last_name__icontains=search) | Q(user__first_name__icontains=search) | Q(user__username__icontains=search)
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
    return render(request, 'enseignement/matiere_form.html', {'form': form})


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
    return render(request, 'enseignement/matiere_form.html', {'form': form})


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
    if not request.user.has_module_permission('professeur_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des professeurs.")
        return redirect('enseignement:professeur_list')
    
    if request.method == 'POST':
        user_id = request.POST.get('user')
        statut = request.POST.get('statut', 'actif')
        matiere_id = request.POST.get('specialite')
        
        if user_id:
            user = get_object_or_404(Utilisateur, pk=user_id)
            prof = ProfilProfesseur.objects.create(
                user=user,
                statut=statut,
                specialite_id=matiere_id
            )
            messages.success(request, f'Profil professeur créé pour {user.get_full_name()}.')
            return redirect('enseignement:professeur_list')
    
    utilisateurs = Utilisateur.objects.filter(role='professeur', profil_professeur__isnull=True)
    matieres = Matiere.objects.all()
    return render(request, 'enseignement/professeur_form.html', {
        'utilisateurs': utilisateurs,
        'matieres': matieres
    })


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
def contrainte_list(request):
    if not request.user.has_module_permission('contrainte_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les contraintes.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    contraintes = ContrainteHoraire.objects.select_related('classe', 'professeur').filter(annee_scolaire=annee) if annee else ContrainteHoraire.objects.none()
    
    return render(request, 'enseignement/contrainte_list.html', {'contraintes': contraintes, 'annee': annee})


@login_required
def emploi_du_temps(request):
    if not request.user.has_module_permission('emploi_du_temps', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les emplois du temps.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    classes = Classe.objects.filter(annee_scolaire=annee) if annee else []
    
    return render(request, 'enseignement/emploi_du_temps.html', {'classes': classes, 'annee': annee})
