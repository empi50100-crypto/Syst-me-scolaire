from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import models
from django.db.models import Avg, Q, Count, Sum
from django.http import HttpResponse
from django.core.paginator import Paginator
from datetime import datetime, date
from academics.models import Classe, Matiere, Enseignement, Evaluation, FicheNote, Salle, CoefficientMatiere, Examen, ContrainteHoraire, Professeur
from academics.forms import ClasseForm, MatiereForm, EnseignementForm, EvaluationForm, SalleForm, CoefficientMatiereForm, ExamenForm, ContrainteHoraireForm
from authentification.models import DemandeApprobation, Notification, User


def is_direction_or_secretaire(user):
    return user.is_authenticated and (user.is_direction() or user.is_secretaire() or user.is_superadmin())


def is_direction_or_superadmin(user):
    return user.is_authenticated and (user.is_direction() or user.is_superadmin() or user.is_secretaire())


def is_professeur(user):
    return user.is_authenticated and hasattr(user, 'professeur') and user.professeur is not None


@login_required
def classe_list_view(request):
    if not request.user.has_module_permission('classe_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les classes.")
        return redirect('dashboard')
    
    from finances.models import AnneeScolaire
    
    annee_active = AnneeScolaire.objects.filter(est_active=True).first()
    classes_qs = Classe.objects.select_related('annee_scolaire').prefetch_related('inscriptions', 'matieres').order_by('niveau', 'nom', 'subdivision')
    
    # Get parameters
    search = request.GET.get('search', '')
    niveau = request.GET.get('niveau', '')
    annee_id = request.GET.get('annee', str(annee_active.id) if annee_active else '')
    subdivision = request.GET.get('subdivision', '')
    serie = request.GET.get('serie', '')
    
    if search:
        classes_qs = classes_qs.filter(
            Q(nom__icontains=search)
        )
    if niveau:
        classes_qs = classes_qs.filter(niveau=niveau)
    if annee_id:
        classes_qs = classes_qs.filter(annee_scolaire_id=annee_id)
    if subdivision:
        classes_qs = classes_qs.filter(subdivision__icontains=subdivision)
    if serie:
        classes_qs = classes_qs.filter(serie=serie)
    annees = AnneeScolaire.objects.all().order_by('-date_debut')
    niveaux = Classe.Niveau.choices
    series = Classe.Serie.choices
    
    return render(request, 'academics/classe_list.html', {
        'classes': classes_qs,
        'search': search,
        'niveau_filter': niveau,
        'annee_filter': annee_id,
        'subdivision_filter': subdivision,
        'serie_filter': serie,
        'annees': annees,
        'niveaux': niveaux,
        'series': series
    })


@login_required
def matiere_list_view(request):
    if not request.user.has_module_permission('matiere_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les matieres.")
        return redirect('dashboard')
    
    matieres = Matiere.objects.all().order_by('nom')
    
    search = request.GET.get('search', '')
    if search:
        matieres = matieres.filter(nom__icontains=search)
    
    return render(request, 'academics/matiere_list.html', {
        'matieres': matieres,
        'search': search,
    })


@login_required
def professeur_list_view(request):
    if not request.user.has_module_permission('professeur_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les professeurs.")
        return redirect('dashboard')
    
    from academics.models import Professeur
    professors =Professeur.objects.select_related('user').order_by('nom', 'prenom')
    
    search = request.GET.get('search', '')
    if search:
        professors = professors.filter(
            Q(nom__icontains=search) | Q(prenom__icontains=search) | Q(user__username__icontains=search)
        )
    
    return render(request, 'academics/professeur_list.html', {
        'professeurs': professors,
        'search': search,
    })


@login_required
def classe_create_view(request):
    if not request.user.has_module_permission('classe_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de créer des classes.")
        return redirect('academics:classe_list')
    
    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classe creee avec succes.')
            return redirect('academics:classe_list')
    else:
        form = ClasseForm()
    return render(request, 'academics/classe_form.html', {'form': form})


@login_required
def classe_edit_view(request, pk):
    if not request.user.has_module_permission('classe_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des classes.")
        return redirect('academics:classe_list')
    
    classe = get_object_or_404(Classe, pk=pk)
    
    from eleves.models import Inscription
    from finances.models import AnneeScolaire
    annee_active = AnneeScolaire.objects.filter(est_active=True).first()
    
    matieres_avant = ", ".join([str(m) for m in classe.matieres.all()]) if classe.matieres.exists() else "Aucune"
    
    eleves_avant = "Aucun"
    if annee_active:
        eleves_inscrits = Inscription.objects.filter(classe=classe, annee_scolaire=annee_active).select_related('eleve')
        eleves_avant = ", ".join([e.eleve.nom_complet for e in eleves_inscrits]) if eleves_inscrits.exists() else "Aucun"
    
    details_avant = f"""Etat actuel de la classe:
- Nom: {classe.nom}
- Niveau: {classe.get_niveau_display() if hasattr(classe, 'get_niveau_display') else getattr(classe, 'niveau', '')}
- Série: {classe.get_serie_display() if hasattr(classe, 'get_serie_display') else getattr(classe, 'serie', '')}
- Domaine: {classe.domaine}
- Matières: {matieres_avant}
- Élèves: {eleves_avant}"""

    if request.method == 'POST':
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid():
            if request.user.is_superadmin() or request.user.is_direction():
                form.save()
                messages.success(request, 'Classe modifiée avec succès.')
                return redirect('academics:classe_list')
            else:
                classe_updated = form.save(commit=False)
                demande = DemandeApprobation.objects.create(
                    demandeur=request.user,
                    type_action=DemandeApprobation.TypeAction.MODIFICATION,
                    type_objet=DemandeApprobation.TypeObjet.CLASSE,
                    objet_id=classe.pk,
                    objet_repr=str(classe),
                    details=f"Demande de modification de la classe {classe.nom}",
                    details_avant=details_avant,
                    details_apos="Modification demandée"
                )
                messages.success(request, 'Votre demande a été soumise.')
                return redirect('academics:classe_list')
    else:
        form = ClasseForm(instance=classe)
    
    return render(request, 'academics/classe_form.html', {'form': form, 'classe': classe})


@login_required
def classe_delete_view(request, pk):
    if not request.user.has_module_permission('classe_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des classes.")
        return redirect('academics:classe_list')
    
    classe = get_object_or_404(Classe, pk=pk)
    if request.method == 'POST':
        if request.user.is_superadmin() or request.user.is_direction():
            classe.delete()
            messages.success(request, 'Classe supprimée avec succès.')
            return redirect('academics:classe_list')
        else:
            messages.success(request, 'Votre demande a été soumise.')
            return redirect('academics:classe_list')
    
    return render(request, 'academics/classe_confirm_delete.html', {'classe': classe})


@login_required
def view_func(request):
    matieres = Matiere.objects.all().order_by('nom')
    return render(request, 'academics/matiere_list.html', {'matieres': matieres})


@login_required
def matiere_create_view(request):
    if not request.user.has_module_permission('matiere_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des matières.")
        return redirect('academics:matiere_list')
    
    if request.method == 'POST':
        form = MatiereForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matiere creee avec succes.')
            return redirect('academics:matiere_list')
    else:
        form = MatiereForm()
    return render(request, 'academics/matiere_form.html', {'form': form})


@login_required
def matiere_edit_view(request, pk):
    if not request.user.has_module_permission('matiere_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des matières.")
        return redirect('academics:matiere_list')
    
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        form = MatiereForm(request.POST, instance=matiere)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matiere modifiee avec succes.')
            return redirect('academics:matiere_list')
    else:
        form = MatiereForm(instance=matiere)
    return render(request, 'academics/matiere_form.html', {'form': form})


@login_required
def matiere_delete_view(request, pk):
    if not request.user.has_module_permission('matiere_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des matières.")
        return redirect('academics:matiere_list')
    
    matiere = get_object_or_404(Matiere, pk=pk)
    if request.method == 'POST':
        matiere.delete()
        messages.success(request, 'Matiere supprimee avec succes.')
        return redirect('academics:matiere_list')
    return render(request, 'academics/matiere_confirm_delete.html', {'matiere': matiere})


@login_required
def salle_list_view(request):
    from django.db.models import Max
    profes_ids = Enseignement.objects.values_list('professeur_id', flat=True).distinct()
    profes = []
    for pid in profes_ids:
        ens = Enseignement.objects.filter(professeur_id=pid).first()
        if ens and ens.professeur:
            profes.append(ens.professeur)
    profes = sorted(profes, key=lambda p: (p.nom or '', p.prenom or ''))
    return render(request, 'academics/professeur_list.html', {'professeurs': profes})


@login_required
def professeur_create_view(request):
    if not request.user.has_module_permission('professeur_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des professeurs.")
        return redirect('academics:professeur_list')
    
    from academics.forms import ProfesseurForm
    if request.method == 'POST':
        form = ProfesseurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Professeur cree avec succes.')
            return redirect('academics:professeur_list')
    else:
        form = ProfesseurForm()
    
    is_direction = request.user.is_direction()
    is_secretaire = request.user.is_secretaire()
    is_compta = hasattr(request.user, 'is_compta') and request.user.is_compta()
    
    return render(request, 'academics/professeur_form.html', {
        'form': form,
        'is_direction_or_compta': is_direction or is_compta,
        'is_secretaire': is_secretaire,
    })


@login_required
def professeur_edit_view(request, pk):
    if not request.user.has_module_permission('professeur_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des professeurs.")
        return redirect('academics:professeur_list')
    
    from academics.models import Enseignement, Professeur
    from academics.forms import ProfesseurForm
    prof = get_object_or_404(Professeur, pk=pk)
    
    if request.method == 'POST':
        form = ProfesseurForm(request.POST, instance=prof)
        if form.is_valid():
            form.save()
            messages.success(request, 'Professeur modifié avec succès.')
            return redirect('academics:professeur_list')
    else:
        form = ProfesseurForm(instance=prof)
    
    is_direction = request.user.is_direction()
    is_secretaire = request.user.is_secretaire()
    is_compta = hasattr(request.user, 'is_compta') and request.user.is_compta()
    
    return render(request, 'academics/professeur_form.html', {
        'form': form,
        'professeur': prof,
        'is_direction_or_compta': is_direction or is_compta,
        'is_secretaire': is_secretaire,
    })


@login_required
def professeur_delete_view(request, pk):
    if not request.user.has_module_permission('professeur_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des professeurs.")
        return redirect('academics:professeur_list')
    
    from academics.models import Professeur
    prof = get_object_or_404(Professeur, pk=pk)
    if request.method == 'POST':
        prof.delete()
        messages.success(request, 'Professeur supprimé avec succès.')
        return redirect('academics:professeur_list')
    return render(request, 'academics/professeur_confirm_delete.html', {'prof': prof})


@login_required
def view_func(request):
    enseignements = Enseignement.objects.all().select_related('professeur', 'classe', 'matiere', 'annee_scolaire')
    print(f"Total enseignements: {enseignements.count()}")
    for e in enseignements:
        print(f"  {e} - horaires: {e.horaires}")
    return render(request, 'academics/attribution_list.html', {'Professeurs': enseignements})


@login_required
def attribution_list_view(request):
    if not request.user.has_module_permission('attribution_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de créer des attributions.")
        return redirect('academics:attribution_list')
    
    if request.method == 'POST':
        print("POST data:", request.POST)
        form = EnseignementForm(request.POST)
        print("Form is valid:", form.is_valid())
        if not form.is_valid():
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")        
        if form.is_valid():
            enseignement = form.save(commit=False)
            horaires_json = request.POST.get('horaires_json', '[]')
            print("horaires_json:", horaires_json)
            try:
                import json
                enseignements_data = json.loads(horaires_json)
                enseignement.horaires = enseignements_data
                print("Parsed horaires:", enseignements_data)
            except Exception as e:
                print(f"Error parsing horaires: {e}")
                enseignement.horaires = []
            
            conflits = []
            if hasattr(enseignment, 'professeur') and enseignement.horaires:
                from academics.models import ContrainteHoraire
                for h in enseignement.horaires:
                    contraintes = ContrainteHoraire.objects.filter(
                        professeur=enseignment.professeur,
                        jour=h.get('jour', '')
                    )
                    for contrainte in contraintes:
                        if contrainte.heure_debut and contrainte.heure_fin:
                            h_debut = h.get('heure_debut', '')
                            h_fin = h.get('heure_fin', '')
                            if h_debut and h_fin:
                                if not (h_fin <= contrainte.heure_debut.strftime('%H:%M') or h_debut >= contrainte.heure_fin.strftime('%H:%M')):
                                    conflits.append(f"{contrainte.get_jour_display()} {contrainte.heure_debut.strftime('%H:%M')}-{contrainte.heure_fin.strftime('%H:%M')} ({contrainte.get_type_contrainte_display()})")
            
            if conflits:
                messages.error(request, f"Conflit detected avec les contraintes: {', '.join(conflits)}. Veuillez ajuster les horaires.")
                return render(request, 'academics/attribution_form.html', {'form': form})
            
            try:
                enseignement.save()
                messages.success(request, 'Attribution creee avec succes.')
                return redirect('academics:attribution_list')
            except Exception as e:
                error_msg = str(e)
                if "Existence" in error_msg or "exists" in error_msg.lower():
                    messages.error(request, 'Une attribution pour ce professeur existe déjà.')
                else:
                    messages.error(request, f'Erreur lors de la sauvegarde: {e}')
                print(f"Save error: {e}")
    else:
        form = EnseignementForm()
        return render(request, 'academics/attribution_form.html', {'form': form})


@login_required
def attribution_edit_view(request, pk):
    if not request.user.has_module_permission('attribution_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des attributions.")
        return redirect('academics:attribution_list')
    
    ens = get_object_or_404(Enseignement, pk=pk)
    if request.method == 'POST':
        form = EnseignementForm(request.POST, instance=ens)
        if form.is_valid():
            ens_updated = form.save(commit=False)
            horaires_json = request.POST.get('horaires_json', '[]')
            try:
                import json
                ens_updated.horaires = json.loads(horaires_json)
            except:
                ens_updated.horaires = []
            ens_updated.save()
            messages.success(request, 'Attribution modifiee avec succes.')
            return redirect('academics:attribution_list')
    else:
        form = EnseignementForm(instance=ens)
        return render(request, 'academics/attribution_form.html', {'form': form, 'horaires': ens.horaires})


@login_required
def attribution_delete_view(request, pk):
    if not request.user.has_module_permission('attribution_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des attributions.")
        return redirect('academics:attribution_list')
    
    enseignement = get_object_or_404(Enseignement, pk=pk)
    if request.method == 'POST':
        enseignement.delete()
        messages.success(request, 'Attribution supprimee avec succes.')
        return redirect('academics:attribution_list')
    return render(request, 'academics/attribution_confirm_delete.html', {'enseignant': enseignement})


@login_required
def mes_classes_view(request):
    if not hasattr(request.user, 'professeur') or not request.user.professeur:
        messages.error(request, "Vous n'etes pas lie a un professeur.")
        return redirect('dashboard')
    
    from finances.models import AnneeScolaire
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    enseignements = Enseignement.objects.filter(
        professeur=request.user.professeur,
        classe__annee_scolaire=annee
    ).select_related('classe', 'matiere', 'annee_scolaire')
    
    return render(request, 'academics/mes_classes.html', {'enseignements': enseignements})


@login_required
def saisie_notes(request):
    if not request.user.has_module_permission('saisie_notes', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des évaluations.")
        return redirect('academics:saisie_notes')
    
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evaluation creee avec succes.')
            return redirect('academics:saisie_notes')
    else:
        form = EvaluationForm()
        if hasattr(request.user, 'professeur') and request.user.professeur:
            form.fields['professeur'].queryset = type('ens', (), {'objects': type('', (), {'filter': lambda self, **k: type('', (), {'all': lambda: []})()})()})()
    
    return render(request, 'academics/evaluation_form.html', {'form': form})


@login_required
def evaluation_edit_view(request, pk):
    if not request.user.has_module_permission('saisie_notes', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des évaluations.")
        return redirect('academics:saisie_notes')
    
    evaluation = get_object_or_404(Evaluation, pk=pk)
    
    from finances.models import AnneeScolaire
    from eleves.models import Inscription
    
    annee = evaluation.annee_scolaire
    
    ens = evaluation.matiere.enseignements.filter(classe__annee_scolaire=annee).first()
    selected_classe = ens.classe if ens else None
    
    all_evals = list(Evaluation.objects.filter(
        matiere=evaluation.matiere,
        type_eval=evaluation.type_eval,
        date_eval=evaluation.date_eval,
        titre=evaluation.titre,
        annee_scolaire=annee
    ).select_related('eleve'))
    
    eleves_data = []
    if selected_classe:
        inscriptions = Inscription.objects.filter(
            classe=selected_classe,
            annee_scolaire=annee
        ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom')
        
        eval_by_eleve = {ev.eleve_id: ev for ev in all_evals}
        
        for inscription in inscriptions:
            ev = eval_by_eleve.get(inscription.eleve_id)
            eleves_data.append({
                'eleve': inscription.eleve,
                'note': float(ev.note) if ev else None,
                'observations': ev.observations if ev else '',
                'eval_id': ev.pk if ev else None,
            })
    else:
        for ev in all_evals:
            eleves_data.append({
                'eleve': ev.eleve,
                'note': float(ev.note),
                'observations': ev.observations,
                'eval_id': ev.pk,
            })
    
    if request.method == 'POST':
        type_eval = request.POST.get('type_eval')
        titre = request.POST.get('titre', '')
        date_eval = request.POST.get('date_eval')
        
        if not type_eval or not date_eval:
            messages.error(request, "Le type et la date sont obligatoires.")
            return render(request, 'academics/evaluation_form.html', {
                'form': None,
                'evaluation': evaluation,
                'eleves_data': eleves_data,
                'type_eval': type_eval,
                'titre': titre,
                'date_eval': date_eval,
                'selected_matiere': evaluation.matiere,
                'selected_classe': selected_classe,
            })
        
        # Déterminer la période automatiquement en fonction des clotures
        periode = 1  # Par défaut
        if selected_classe:
            from eleves.models import PeriodeCloture
            from finances.models import AnneeScolaire
            
            p1_cloture = PeriodeCloture.objects.filter(classe=selected_classe, periode=1).exists()
            if p1_cloture:
                p2_cloture = PeriodeCloture.objects.filter(classe=selected_classe, periode=2).exists()
                if p2_cloture:
                    if annee.type_cycle_actif == 'trimestriel':
                        p3_cloture = PeriodeCloture.objects.filter(classe=selected_classe, periode=3).exists()
                        periode = 3 if p3_cloture else 3
                    else:
                        periode = 2
                else:
                    periode = 2
        else:
            periode = 1
        
        updated_count = 0
        for key, value in request.POST.items():
            if key.startswith('note_eleve_'):
                eleve_id = key.replace('note_eleve_', '')
                note_str = value.strip()
                eval_id = request.POST.get(f'eval_id_{eleve_id}')
                observation = request.POST.get(f'observation_eleve_{eleve_id}', '').strip()
                
                if note_str:
                    try:
                        note = float(note_str)
                        if 0 <= note <= 20:
                            if eval_id:
                                ev = Evaluation.objects.filter(pk=eval_id).first()
                                if ev:
                                    ev.note = note
                                    ev.observations = observation
                                    ev.save()
                                    updated_count += 1
                            else:
                                Evaluation.objects.create(
                                    eleve_id=eleve_id,
                                    matiere=evaluation.matiere,
                                    type_eval=type_eval,
                                    titre=titre,
                                    date_eval=date_eval,
                                    note=note,
                                    coefficient=evaluation.matiere.coefficient or 1,
                                    annee_scolaire=annee,
                                    observations=observation,
                                    periode=periode,
                                )
                                updated_count += 1
                    except ValueError:
                        pass
        
        messages.success(request, f'{updated_count} note(s) mise(s) à jour.')
        
        if selected_classe:
            return redirect('academics:saisie_notes_detail', classe_pk=selected_classe.pk, matiere_pk=evaluation.matiere.pk)
        return redirect('academics:saisie_notes')
    
    return render(request, 'academics/evaluation_form.html', {
        'form': None,
        'evaluation': evaluation,
        'eleves_data': eleves_data,
        'type_eval': evaluation.type_eval,
        'titre': evaluation.titre,
        'date_eval': evaluation.date_eval,
        'selected_matiere': evaluation.matiere,
        'selected_classe': selected_classe,
    })


@login_required
def evaluation_delete_view(request, pk):
    if not request.user.has_module_permission('saisie_notes', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des évaluations.")
        return redirect('academics:saisie_notes')
    
    evaluation = get_object_or_404(Evaluation, pk=pk)
    
    deleted_count = Evaluation.objects.filter(
        matiere=evaluation.matiere,
        type_eval=evaluation.type_eval,
        date_eval=evaluation.date_eval,
        titre=evaluation.titre,
        annee_scolaire=evaluation.annee_scolaire
    ).count()
    
    Evaluation.objects.filter(
        matiere=evaluation.matiere,
        type_eval=evaluation.type_eval,
        date_eval=evaluation.date_eval,
        titre=evaluation.titre,
        annee_scolaire=evaluation.annee_scolaire
    ).delete()
    
    messages.success(request, f'{deleted_count} évaluation(s) supprimée(s).')
    
    classe_pk = evaluation.matiere.enseignements.filter(classe__annee_scolaire=evaluation.annee_scolaire).first().classe.pk if evaluation.matiere.enseignements.filter(classe__annee_scolaire=evaluation.annee_scolaire).exists() else None
    if classe_pk:
        return redirect('academics:saisie_notes_detail', classe_pk=classe_pk, matiere_pk=evaluation.matiere.pk)
    return redirect('academics:saisie_notes')


@login_required
def saisie_notes_detail_view(request, classe_pk=None, matiere_pk=None):
    from finances.models import AnneeScolaire, CycleConfig
    from eleves.models import Inscription
    
    if not request.user.has_module_permission('saisie_notes', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les notes.")
        return redirect('academics:mes_classes')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, "Aucune annee scolaire active.")
        return redirect('dashboard')
    
    classes = []
    if hasattr(request.user, 'professeur') and request.user.professeur:
        enseignements = Enseignement.objects.filter(
            classe__annee_scolaire=annee,
            professeur=request.user.professeur
        ).select_related('classe')
        classes = list({ens.classe for ens in enseignements})
    else:
        classes = list(Classe.objects.filter(annee_scolaire=annee))
    
    selected_classe = None
    selected_matiere = None
    eleves = []
    evaluations = []
    matieres = []
    cycles = list(CycleConfig.objects.filter(annee_scolaire=annee).order_by('date_debut'))
    evaluations_by_date = []
    eleves_data = []
    evaluations_grouped = {}
    stats = {}
    
    type_filter = request.GET.get('type_eval', '')
    cycle_filter = request.GET.get('cycle', '')
    date_filter = request.GET.get('date', '')
    
    if classe_pk:
        selected_classe = get_object_or_404(Classe, pk=classe_pk)
        eleves = list(Inscription.objects.filter(
            classe=selected_classe,
            annee_scolaire=annee
        ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom'))
        
        if hasattr(request.user, 'professeur') and request.user.professeur:
            enseignements = Enseignement.objects.filter(
                classe=selected_classe,
                professeur=request.user.professeur
            ).select_related('matiere')
            matieres = [ens.matiere for ens in enseignements]
        else:
            matieres = list(Matiere.objects.filter(
                enseignements__classe=selected_classe
            ).distinct())
        
        if matiere_pk:
            selected_matiere = get_object_or_404(Matiere, pk=matiere_pk)
            evaluations_qs = Evaluation.objects.filter(
                matiere=selected_matiere,
                annee_scolaire=annee
            ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom', 'date_eval')
            
            if type_filter:
                evaluations_qs = evaluations_qs.filter(type_eval=type_filter)
            if cycle_filter:
                cycle = CycleConfig.objects.filter(pk=cycle_filter, annee_scolaire=annee).first()
                if cycle:
                    evaluations_qs = evaluations_qs.filter(
                        date_eval__gte=cycle.date_debut,
                        date_eval__lte=cycle.date_fin
                    )
            if date_filter:
                evaluations_qs = evaluations_qs.filter(date_eval=date_filter)
            
            evaluations = list(evaluations_qs)
            
            from collections import defaultdict
            eval_by_date = defaultdict(list)
            for ev in evaluations:
                eval_by_date[ev.date_eval].append(ev)
            evaluations_by_date = [{'date': d, 'evals': v, 'count': len(v), 'eval_id': v[0].pk if v else None} for d, v in sorted(eval_by_date.items())]
            
            eleves_data = []
            eleve_ids = [e.eleve_id for e in eleves]
            eval_by_eleve = {}
            for ev in evaluations:
                if ev.eleve_id not in eval_by_eleve:
                    eval_by_eleve[ev.eleve_id] = []
                eval_by_eleve[ev.eleve_id].append(ev)
            
            for inscription in eleves:
                evals = eval_by_eleve.get(inscription.eleve_id, [])
                grouped = {
                    'interrogation': [e for e in evals if e.type_eval == 'interrogation'],
                    'mini_devoir': [e for e in evals if e.type_eval == 'mini_devoir'],
                    'devoir': [e for e in evals if e.type_eval == 'devoir'],
                    'examen': [e for e in evals if e.type_eval == 'examen'],
                }
                
                type_avgs = []
                for evals_type in grouped.values():
                    if evals_type:
                        avg = sum(float(e.note) for e in evals_type) / len(evals_type)
                        type_avgs.append(round(avg, 2))
                
                if type_avgs:
                    student_avg = round(sum(type_avgs) / len(type_avgs), 2)
                else:
                    student_avg = None
                
                eleves_data.append({
                    'inscription': inscription,
                    'eleve': inscription.eleve,
                    'evaluations': evals,
                    'grouped': grouped,
                    'last_note': evals[-1].note if evals else None,
                    'count': len(evals),
                    'student_avg': student_avg,
                })
            
            evaluations_grouped = {
                'interrogation': [e for e in evaluations if e.type_eval == 'interrogation'],
                'mini_devoir': [e for e in evaluations if e.type_eval == 'mini_devoir'],
                'devoir': [e for e in evaluations if e.type_eval == 'devoir'],
                'examen': [e for e in evaluations if e.type_eval == 'examen'],
            }
            
            coef = float(selected_matiere.coefficient or 1)
            stats = {}
            
            if type_filter:
                filtered_evals = evaluations
                stats['global'] = {
                    'count': len(filtered_evals),
                    'min': min((float(e.note) for e in filtered_evals), default=0),
                    'max': max((float(e.note) for e in filtered_evals), default=0),
                    'avg': round(sum(float(e.note) for e in filtered_evals) / len(filtered_evals), 2) if filtered_evals else 0,
                }
                
                for type_name, evals in evaluations_grouped.items():
                    if type_name == type_filter and evals:
                        notes = [float(e.note) for e in evals]
                        stats[type_name] = {
                            'count': len(notes),
                            'min': min(notes),
                            'max': max(notes),
                            'avg': round(sum(notes) / len(notes), 2),
                        }
            else:
                for type_name, evals in evaluations_grouped.items():
                    if evals:
                        notes = [float(e.note) for e in evals]
                        stats[type_name] = {
                            'count': len(notes),
                            'min': min(notes),
                            'max': max(notes),
                            'avg': round(sum(notes) / len(notes), 2),
                        }
                
                all_notes = [float(e.note) for e in evaluations]
                stats['global'] = {
                    'count': len(all_notes),
                    'min': min(all_notes) if all_notes else 0,
                    'max': max(all_notes) if all_notes else 0,
                    'avg': round(sum(all_notes) / len(all_notes), 2) if all_notes else 0,
                }
            
            eleves_data = eleves_data
        else:
            eleves_data = []
            evaluations_grouped = {}
            stats = {}
            eleves_data = []
            evaluations_grouped = {}
            stats = {}
    
    if request.method == 'POST' and selected_classe and selected_matiere:
        if not request.user.has_module_permission('saisie_notes', 'write'):
            messages.error(request, "Vous n'avez pas l'autorisation de modifier les notes.")
            return redirect('academics:saisie_notes_detail', classe_pk=classe_pk, matiere_pk=matiere_pk)
        
        type_eval = request.POST.get('type_eval')
        titre = request.POST.get('titre', '')
        date_eval = request.POST.get('date_eval')
        
        if not type_eval:
            messages.error(request, "Le type d'évaluation est obligatoire.")
            return redirect('academics:saisie_notes_detail', classe_pk=classe_pk, matiere_pk=matiere_pk)
        
        if not date_eval:
            messages.error(request, "La date d'évaluation est obligatoire.")
            return redirect('academics:saisie_notes_detail', classe_pk=classe_pk, matiere_pk=matiere_pk)
        
        saved_count = 0
        errors = []
        
        # Déterminer la période automatiquement en fonction des clotures
        periode = 1  # Par défaut
        if selected_classe:
            from eleves.models import PeriodeCloture
            from finances.models import AnneeScolaire
            
            annee = AnneeScolaire.objects.filter(est_active=True).first()
            
            p1_cloture = PeriodeCloture.objects.filter(classe=selected_classe, periode=1).exists()
            if p1_cloture:
                p2_cloture = PeriodeCloture.objects.filter(classe=selected_classe, periode=2).exists()
                if p2_cloture:
                    if annee and annee.type_cycle_actif == 'trimestriel':
                        p3_cloture = PeriodeCloture.objects.filter(classe=selected_classe, periode=3).exists()
                        periode = 3 if p3_cloture else 3
                    else:
                        periode = 2
                else:
                    periode = 2
            else:
                periode = 1
        
        for key, value in request.POST.items():
            if key.startswith('note_eleve_'):
                eleve_id = key.replace('note_eleve_', '')
                note_str = value.strip()
                
                if not note_str:
                    continue
                
                try:
                    note = float(note_str)
                    if note < 0 or note > 20:
                        errors.append(f"Note {note} invalide pour l'élève {eleve_id} (doit être entre 0 et 20)")
                        continue
                    
                    observation_key = f'observation_eleve_{eleve_id}'
                    observation = request.POST.get(observation_key, '').strip()
                    
                    Evaluation.objects.create(
                        eleve_id=eleve_id,
                        matiere=selected_matiere,
                        type_eval=type_eval,
                        titre=titre,
                        date_eval=date_eval,
                        note=note,
                        coefficient=selected_matiere.coefficient or 1,
                        annee_scolaire=annee,
                        observations=observation,
                        periode=periode,
                    )
                    saved_count += 1
                    
                except ValueError:
                    errors.append(f"Note invalide '{note_str}' pour l'élève {eleve_id}")
        
        if saved_count > 0:
            messages.success(request, f'{saved_count} note(s) enregistrée(s) avec succès.')
        for err in errors:
            messages.error(request, err)
        return redirect('academics:saisie_notes_detail', classe_pk=classe_pk, matiere_pk=matiere_pk)
    
    return render(request, 'academics/saisie_notes.html', {
        'classes': classes,
        'matieres': matieres,
        'cycles': cycles,
        'selected_classe': selected_classe,
        'selected_matiere': selected_matiere,
        'eleves': eleves,
        'eleves_data': eleves_data,
        'evaluations': evaluations,
        'evaluations_by_date': evaluations_by_date,
        'evaluations_grouped': evaluations_grouped,
        'stats': stats,
        'type_filter': type_filter,
        'cycle_filter': cycle_filter,
        'date_filter': date_filter,
    })


@login_required
def bulletin_view(request, classe_pk):
    from finances.models import AnneeScolaire, CycleConfig
    from eleves.models import Inscription
    
    if not request.user.has_module_permission('saisie_notes', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les notes.")
        return redirect('academics:saisie_notes')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, "Aucune annee scolaire active.")
        return redirect('dashboard')
    
    classe = get_object_or_404(Classe, pk=classe_pk)
    
    if hasattr(request.user, 'professeur') and request.user.professeur:
        enseignements = Enseignement.objects.filter(
            classe=classe,
            professeur=request.user.professeur
        ).select_related('matiere')
        matieres = [ens.matiere for ens in enseignements]
    else:
        matieres = list(Matiere.objects.filter(
            enseignements__classe=classe
        ).distinct())
    
    eleves = list(Inscription.objects.filter(
        classe=classe,
        annee_scolaire=annee
    ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom'))
    
    cycles = list(CycleConfig.objects.filter(annee_scolaire=annee).order_by('date_debut'))
    selected_cycle_pk = request.GET.get('cycle')
    selected_cycle = None
    if selected_cycle_pk:
        selected_cycle = next((c for c in cycles if str(c.pk) == selected_cycle_pk), None)
    elif cycles:
        selected_cycle = cycles[0]
    
    eleves_data = []
    for inscription in eleves:
        eleves_notes = {}
        for matiere in matieres:
            evals = list(Evaluation.objects.filter(
                eleve=inscription.eleve,
                matiere=matiere,
                annee_scolaire=annee
            ))
            
            if selected_cycle:
                evals = [e for e in evals if selected_cycle.date_debut <= e.date_eval <= selected_cycle.date_fin]
            
            grouped = {
                'interrogation': [e for e in evals if e.type_eval == 'interrogation'],
                'mini_devoir': [e for e in evals if e.type_eval == 'mini_devoir'],
                'devoir': [e for e in evals if e.type_eval == 'devoir'],
                'examen': [e for e in evals if e.type_eval == 'examen'],
            }
            
            type_avgs = []
            for evals_type in grouped.values():
                if evals_type:
                    avg = sum(float(e.note) for e in evals_type) / len(evals_type)
                    type_avgs.append(round(avg, 2))
            
            coef = float(matiere.coefficient or 1)
            if type_avgs:
                moyenne_sur_20 = round(sum(type_avgs) / len(type_avgs), 2)
                moyenne_coef = round(moyenne_sur_20 * coef, 2)
            else:
                moyenne_sur_20 = None
                moyenne_coef = None
            
            eleves_notes[matiere.pk] = {
                'grouped': grouped,
                'moyenne_sur_20': moyenne_sur_20,
                'moyenne_coef': moyenne_coef,
                'count': len(evals),
                'last_note': evals[-1].note if evals else None,
            }
        
        eleves_data.append({
            'eleve': inscription.eleve,
            'notes': eleves_notes,
        })
    
    total_coef = sum(float(m.coefficient or 1) for m in matieres)
    eleves_with_avg = []
    for item in eleves_data:
        total_moy_coef = sum(
            v['moyenne_coef'] for v in item['notes'].values() if v['moyenne_coef']
        )
        moy_gen = round(total_moy_coef / total_coef, 2) if total_moy_coef > 0 else None
        eleves_with_avg.append({
            **item,
            'moyenne_generale': moy_gen,
            'total_moy_coef': total_moy_coef,
        })
    
    eleves_with_avg.sort(key=lambda x: x['moyenne_generale'] or 0, reverse=True)
    for i, item in enumerate(eleves_with_avg):
        item['rang'] = i + 1
    
    return render(request, 'academics/feuille_notes.html', {
        'classe': classe,
        'matieres': matieres,
        'cycles': cycles,
        'selected_cycle': selected_cycle,
        'eleves_data': eleves_with_avg,
        'total_coef': total_coef,
    })


@login_required
def releve_notes_view(request, classe_pk):
    from finances.models import AnneeScolaire, CycleConfig
    from eleves.models import Inscription
    from django.db.models import Count
    
    if not request.user.has_module_permission('saisie_notes', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, "Aucune annee scolaire active.")
        return redirect('dashboard')
    
    classe = get_object_or_404(Classe, pk=classe_pk)
    cycles = list(CycleConfig.objects.filter(annee_scolaire=annee).order_by('date_debut'))
    selected_cycle_pk = request.GET.get('cycle')
    selected_cycle = None
    if selected_cycle_pk:
        selected_cycle = next((c for c in cycles if str(c.pk) == selected_cycle_pk), None)
    elif cycles:
        selected_cycle = cycles[0]
    
    eleves = list(Inscription.objects.filter(
        classe=classe,
        annee_scolaire=annee
    ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom'))
    
    matieres = list(Matiere.objects.filter(
        enseignements__classe=classe
    ).distinct())
    
    eval_qs = Evaluation.objects.filter(
        matiere__in=matieres,
        annee_scolaire=annee
    )
    if selected_cycle:
        eval_qs = eval_qs.filter(date_eval__gte=selected_cycle.date_debut, date_eval__lte=selected_cycle.date_fin)
    eval_qs = list(eval_qs)
    
    all_notes = [float(e.note) for e in eval_qs]
    
    stats_global = {
        'count': len(all_notes),
        'min': min(all_notes) if all_notes else 0,
        'max': max(all_notes) if all_notes else 0,
        'avg': round(sum(all_notes) / len(all_notes), 2) if all_notes else 0,
        'median': sorted(all_notes)[len(all_notes)//2] if all_notes else 0,
    }
    
    distribution = {'d0_4': 0, 'd5_9': 0, 'd10_14': 0, 'd15_20': 0}
    for n in all_notes:
        if n < 5: distribution['d0_4'] += 1
        elif n < 10: distribution['d5_9'] += 1
        elif n < 15: distribution['d10_14'] += 1
        else: distribution['d15_20'] += 1
    
    stats_matieres = []
    for matiere in matieres:
        matiere_evals = [e for e in eval_qs if e.matiere_id == matiere.pk]
        notes = [float(e.note) for e in matiere_evals]
        coef = float(matiere.coefficient or 1)
        
        grouped = {
            'interrogation': [float(e.note) for e in matiere_evals if e.type_eval == 'interrogation'],
            'mini_devoir': [float(e.note) for e in matiere_evals if e.type_eval == 'mini_devoir'],
            'devoir': [float(e.note) for e in matiere_evals if e.type_eval == 'devoir'],
            'examen': [float(e.note) for e in matiere_evals if e.type_eval == 'examen'],
        }
        
        type_stats = {}
        for type_name, notes_list in grouped.items():
            if notes_list:
                type_stats[type_name] = {
                    'count': len(notes_list),
                    'avg': round(sum(notes_list) / len(notes_list), 2),
                    'min': min(notes_list),
                    'max': max(notes_list),
                }
        
        if notes:
            type_avgs = [sum(v)/len(v) for v in grouped.values() if v]
            moy_sur_20 = round(sum(type_avgs) / len(type_avgs), 2) if type_avgs else 0
            moy_coef = round(moy_sur_20 * coef, 2)
        else:
            moy_sur_20 = 0
            moy_coef = 0
        
        eleves_noted = len(set(e.eleve_id for e in matiere_evals))
        
        stats_matieres.append({
            'matiere': matiere,
            'coef': coef,
            'count': len(notes),
            'eleves_noted': eleves_noted,
            'total_eleves': len(eleves),
            'avg': round(sum(notes) / len(notes), 2) if notes else 0,
            'min': min(notes) if notes else 0,
            'max': max(notes) if notes else 0,
            'moy_sur_20': moy_sur_20,
            'moy_coef': moy_coef,
            'type_stats': type_stats,
        })
    
    total_coef = sum(float(m.coefficient or 1) for m in matieres)
    total_moy_coef = sum(m['moy_coef'] for m in stats_matieres)
    moy_generale = round(total_moy_coef / total_coef, 2) if total_coef > 0 and total_moy_coef > 0 else 0
    
    eleves_stats = []
    for inscription in eleves:
        evals = [e for e in eval_qs if e.eleve_id == inscription.eleve_id]
        eleves_notes = [float(e.note) for e in evals]
        
        matieres_data = []
        total_mc = 0
        for matiere in matieres:
            me = [e for e in evals if e.matiere_id == matiere.pk]
            notes = [float(e.note) for e in me]
            grouped = {
                t: [float(e.note) for e in me if e.type_eval == t]
                for t in ['interrogation', 'mini_devoir', 'devoir', 'examen']
            }
            type_avgs = [sum(v)/len(v) for v in grouped.values() if v]
            m20 = round(sum(type_avgs) / len(type_avgs), 2) if type_avgs else None
            mc = round(m20 * float(matiere.coefficient or 1), 2) if m20 else None
            total_mc += mc or 0
            matieres_data.append({'moyenne': m20, 'moyenne_coef': mc})
        
        moy = round(total_mc / total_coef, 2) if total_coef > 0 and total_mc > 0 else None
        eleves_stats.append({
            'eleve': inscription.eleve,
            'moyenne': moy,
            'count_notes': len(eleves_notes),
        })
    
    eleves_stats.sort(key=lambda x: x['moyenne'] or 0, reverse=True)
    for i, e in enumerate(eleves_stats):
        e['rang'] = i + 1
    
    return render(request, 'academics/statistiques_classe.html', {
        'classe': classe,
        'cycles': cycles,
        'selected_cycle': selected_cycle,
        'matieres': matieres,
        'stats_matieres': stats_matieres,
        'stats_global': stats_global,
        'distribution': distribution,
        'eleves_stats': eleves_stats,
        'total_coef': total_coef,
        'moy_generale': moy_generale,
    })


@login_required
def bulletin_imprimable_view(request, eleve_pk):
    from finances.models import AnneeScolaire, CycleConfig
    from eleves.models import Inscription
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        return render(request, 'academics/bulletin_imprimable.html', {
            'eleve': None, 'classe': None, 'annee': None, 'cycles_data': [],
        })
    
    inscription = get_object_or_404(Inscription, eleve_id=eleve_pk, annee_scolaire=annee)
    eleve = inscription.eleve
    classe = inscription.classe
    
    cycles = CycleConfig.objects.filter(annee_scolaire=annee).order_by('date_debut')
    
    if classe:
        matieres = list(Matiere.objects.filter(
            enseignements__classe=classe,
            enseignements__classe__annee_scolaire=annee
        ).distinct())
    else:
        matieres = []
    
    cycles_data = []
    recap_data = []
    total_coef = 0
    total_moy_coef = 0
    
    from eleves.models import PeriodeCloture
    
    for cycle in cycles:
        matieres_data = []
        cycle_total_coef = 0
        cycle_total_moy_coef = 0
        
        p1_cloture = PeriodeCloture.objects.filter(classe=classe, periode=1).exists() if classe else False
        p2_cloture = PeriodeCloture.objects.filter(classe=classe, periode=2).exists() if classe else False
        
        def get_periode_from_cycle(cycle_numero):
            if cycle_numero == 1:
                return [1]
            elif cycle_numero == 2:
                if not p1_cloture:
                    return []  # Empty until P1 is clotured
                return [2]
            elif cycle_numero == 3:
                if not p1_cloture:
                    return []  # Empty until P1 is clotured
                if not p2_cloture:
                    return []  # Empty until P2 is clotured
                return [3]
            return [cycle_numero]
        
        periodes_to_show = get_periode_from_cycle(cycle.numero)
        
        current_cycle = cycle
        current_periodes = periodes_to_show
        
        for matiere in matieres:
            evals = Evaluation.objects.filter(
                eleve=eleve,
                matiere=matiere,
                annee_scolaire=annee,
                periode__in=periodes_to_show
            )
            
            grouped = {
                'interrogation': list(evals.filter(type_eval='interrogation')),
                'mini_devoir': list(evals.filter(type_eval='mini_devoir')),
                'devoir': list(evals.filter(type_eval='devoir')),
                'examen': list(evals.filter(type_eval='examen')),
            }
            
            type_avgs = []
            for evals_type in grouped.values():
                if evals_type:
                    avg = sum(float(e.note) for e in evals_type) / len(evals_type)
                    type_avgs.append(round(avg, 2))
            
            coef = float(matiere.coefficient or 1)
            
            if type_avgs:
                moyenne_sur_20 = round(sum(type_avgs) / len(type_avgs), 2)
                moyenne_coef = round(moyenne_sur_20 * coef, 2)
            else:
                moyenne_sur_20 = None
                moyenne_coef = None
            
            fiche = FicheNote.objects.filter(eleve=eleve, matiere=matiere, cycle=cycle).first()
            
            matieres_data.append({
                'matiere': matiere,
                'fiche': fiche,
                'moyenne_sur_20': moyenne_sur_20,
                'moyenne_coef': moyenne_coef,
                'coefficient': coef,
                'grouped': grouped,
                'grouped_evals': grouped,
                'interrogation_avg': round(sum(e.note for e in grouped['interrogation']) / len(grouped['interrogation']), 2) if grouped['interrogation'] else None,
                'mini_devoir_avg': round(sum(e.note for e in grouped['mini_devoir']) / len(grouped['mini_devoir']), 2) if grouped['mini_devoir'] else None,
                'devoir_avg': round(sum(e.note for e in grouped['devoir']) / len(grouped['devoir']), 2) if grouped['devoir'] else None,
                'examen_avg': round(sum(e.note for e in grouped['examen']) / len(grouped['examen']), 2) if grouped['examen'] else None,
            })
            
            if moyenne_sur_20 is not None:
                recap_data.append({
                    'matiere': matiere,
                    'cycle': cycle.libelle,
                    'cycle_pk': cycle.pk,
                    'coefficient': coef,
                    'moyenne_sur_20': moyenne_sur_20,
                    'moyenne_coef': moyenne_coef,
                    'rang': fiche.rang if fiche else None,
                })
                cycle_total_coef += coef
                cycle_total_moy_coef += moyenne_coef
                total_coef += coef
                total_moy_coef += moyenne_coef
        
        # Add conduite note for this cycle
        if periodes_to_show:
            from eleves.models import DisciplineEleve, ConduiteConfig
            note_base = 20
            config = ConduiteConfig.objects.filter(
                annee_scolaire=annee,
                niveau=classe.niveau
            ).first()
            if config:
                note_base = float(config.note_base)
            
            disciplines = DisciplineEleve.objects.filter(
                inscription=inscription,
                periode__in=periodes_to_show,
                statut_traitement='traite'
            )
            total_points_discipline = sum(d.points for d in disciplines)
            note_conduite = max(0, min(20, note_base + total_points_discipline))
            
            matieres_data.append({
                'matiere': None,
                'fiche': None,
                'moyenne_sur_20': note_conduite,
                'moyenne_coef': note_conduite * 1,
                'coefficient': 1,
                'grouped_evals': {},
                'is_conduite': True,
                'interrogation_avg': None,
                'mini_devoir_avg': None,
                'devoir_avg': None,
                'examen_avg': None,
            })
            
            cycle_total_coef += 1
            cycle_total_moy_coef += note_conduite
            total_coef += 1
            total_moy_coef += note_conduite
        
        cycle_moyenne = round(cycle_total_moy_coef / cycle_total_coef, 2) if cycle_total_coef > 0 and cycle_total_moy_coef > 0 else None
        
        cycles_data.append({
            'cycle': cycle,
            'matieres_data': matieres_data,
            'total_coef': cycle_total_coef,
            'total_moy_coef': cycle_total_moy_coef,
            'moyenne_cycle': cycle_moyenne,
        })
    
    moyenne_generale = round(total_moy_coef / total_coef, 2) if total_coef > 0 and total_moy_coef > 0 else None
    
    mention = None
    if moyenne_generale is not None:
        if moyenne_generale >= 16: mention = 'EXCELLENT'
        elif moyenne_generale >= 14: mention = 'TRES BIEN'
        elif moyenne_generale >= 12: mention = 'BIEN'
        elif moyenne_generale >= 10: mention = 'PASSABLE'
        else: mention = 'INSUFFISANT'
    
    eleves_count = Inscription.objects.filter(classe=classe, annee_scolaire=annee).count()
    
    matieres_sup_10 = 0
    matieres_inf_10 = 0
    for m in matieres_data:
        if m.get('moyenne_sur_20'):
            if m['moyenne_sur_20'] >= 10:
                matieres_sup_10 += 1
            else:
                matieres_inf_10 += 1
    
    eleves_moyennes = []
    all_inscriptions = Inscription.objects.filter(classe=classe, annee_scolaire=annee).select_related('eleve')
    for ins in all_inscriptions:
        el = ins.eleve
        el_total_points = 0
        el_total_coef = 0
        for matiere in matieres:
            evals = Evaluation.objects.filter(eleve=el, matiere=matiere, annee_scolaire=annee, periode__in=current_periodes)
            if evals.exists():
                type_avgs = []
                for type_eval in ['interrogation', 'mini_devoir', 'devoir', 'examen']:
                    evals_type = list(evals.filter(type_eval=type_eval))
                    if evals_type:
                        type_avgs.append(sum(float(e.note) for e in evals_type) / len(evals_type))
                if type_avgs:
                    moy = round(sum(type_avgs) / len(type_avgs), 2)
                    el_total_points += moy * float(matiere.coefficient or 1)
                    el_total_coef += float(matiere.coefficient or 1)
        if el_total_coef > 0:
            eleves_moyennes.append(round(el_total_points / el_total_coef, 2))
    
    moyenne_classe = round(sum(eleves_moyennes) / len(eleves_moyennes), 2) if eleves_moyennes else None
    
    sorted_eleves = sorted(eleves_moyennes, reverse=True)
    rang = sorted_eleves.index(moyenne_generale) + 1 if moyenne_generale in sorted_eleves else None
    
    return render(request, 'academics/bulletin_pro.html', {
        'eleve': eleve,
        'classe': classe,
        'annee': annee,
        'inscription': inscription,
        'cycles_data': cycles_data,
        'matieres': matieres,
        'matieres_data': matieres_data,
        'moyenne_generale': moyenne_generale,
        'grand_total_coef': total_coef,
        'grand_total_moy_coef': total_moy_coef,
        'recap_data': recap_data,
        'mention': mention,
        'eleves_count': eleves_count,
        'rang': rang,
        'matieres_sup_10': matieres_sup_10,
        'matieres_inf_10': matieres_inf_10,
        'moyenne_classe': moyenne_classe,
        'total_coef': total_coef,
        'total_moy_coef': total_moy_coef,
        'moyenne_cycle': cycle_moyenne,
    })


@login_required
def classe_list(request):
    from finances.models import AnneeScolaire, CycleConfig
    from eleves.models import Inscription
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        return render(request, 'academics/bulletin_classe.html', {'classe': None, 'eleves_data': []})
    
    classe = get_object_or_404(Classe, pk=classe_pk)
    eleves = list(Inscription.objects.filter(
        classe=classe,
        annee_scolaire=annee
    ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom'))
    
    cycles = list(CycleConfig.objects.filter(annee_scolaire=annee).order_by('date_debut'))
    matieres = list(Matiere.objects.filter(
        enseignements__classe=classe,
        enseignements__classe__annee_scolaire=annee
    ).distinct())
    
    total_coef = sum(float(m.coefficient or 1) for m in matieres)
    
    eleves_data = []
    for inscription in eleves:
        eleve = inscription.eleve
        total_moy_coef = 0
        matieres_data = []
        
        for matiere in matieres:
            all_evals = list(Evaluation.objects.filter(
                eleve=eleve,
                matiere=matiere,
                annee_scolaire=annee
            ))
            
            grouped = {
                t: [float(e.note) for e in all_evals if e.type_eval == t]
                for t in ['interrogation', 'mini_devoir', 'devoir', 'examen']
            }
            
            type_avgs = [sum(v)/len(v) for v in grouped.values() if v]
            moy20 = round(sum(type_avgs) / len(type_avgs), 2) if type_avgs else None
            mc = round(moy20 * float(matiere.coefficient or 1), 2) if moy20 else None
            total_moy_coef += mc or 0
            
            matieres_data.append({
                'matiere': matiere,
                'moyenne': moy20,
                'moyenne_coef': mc,
                'coef': float(matiere.coefficient or 1),
            })
        
        moy_gen = round(total_moy_coef / total_coef, 2) if total_coef > 0 and total_moy_coef > 0 else None
        
        mention = None
        if moy_gen is not None:
            if moy_gen >= 16: mention = 'EXCELLENT'
            elif moy_gen >= 14: mention = 'TRES BIEN'
            elif moy_gen >= 12: mention = 'BIEN'
            elif moy_gen >= 10: mention = 'PASSABLE'
            else: mention = 'INSUFFISANT'
        
        eleves_data.append({
            'eleve': eleve,
            'moyenne_generale': moy_gen,
            'total_coef': total_coef,
            'total_moy_coef': total_moy_coef,
            'mention': mention,
            'matieres_data': matieres_data,
        })
    
    eleves_data.sort(key=lambda x: x['moyenne_generale'] or 0, reverse=True)
    for i, item in enumerate(eleves_data):
        item['rang'] = i + 1
    
    return render(request, 'academics/bulletin_classe.html', {
        'classe': classe,
        'annee': annee,
        'cycles': cycles,
        'matieres': matieres,
        'eleves_data': eleves_data,
        'total_coef': total_coef,
    })


@login_required
def saisie_notes(request):
    from finances.models import AnneeScolaire
    
    if not request.user.has_module_permission('saisie_notes', 'read'):
            return redirect('dashboard')    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        return render(request, 'academics/historique_notes.html', {'historique': [], 'classe': None})
    
    classe = None
    if classe_pk:
        classe = get_object_or_404(Classe, pk=classe_pk)
    
    classes = list(Classe.objects.filter(annee_scolaire=annee).order_by('nom'))
    
    eleves_ids = None
    if classe:
        eleves_ids = list(Inscription.objects.filter(
            classe=classe,
            annee_scolaire=annee
        ).values_list('eleve_id', flat=True))
    
    evaluations = list(Evaluation.objects.filter(
        annee_scolaire=annee
    ).select_related('eleve', 'matiere').order_by('-date_eval')[:200])
    
    if eleves_ids is not None:
        evaluations = [e for e in evaluations if e.eleve_id in eleves_ids]
    
    return render(request, 'academics/historique_notes.html', {
        'historique': evaluations,
        'classes': classes,
        'classe': classe,
    })


@login_required
def view_func(request):
    from eleves.models import Inscription
    from finances.models import AnneeScolaire
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        return render(request, 'academics/fiche_notes_list.html', {'eleves': []})
    
    eleves = Inscription.objects.filter(
        annee_scolaire=annee
    ).select_related('eleve', 'classe').order_by('eleve__nom')
    
    return render(request, 'academics/fiche_notes_list.html', {'eleves': eleves})


@login_required
def eleve_list(request, eleve_pk):
    from eleves.models import Inscription
    from finances.models import AnneeScolaire, CycleConfig
    from academics.models import Evaluation, FicheNote
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        return render(request, 'academics/fiche_note_eleve.html', {
            'eleve': None, 'classe': None, 'annee': None, 'cycles_data': [], 'matieres': []
        })
    
    inscription = get_object_or_404(Inscription, eleve_id=eleve_pk, annee_scolaire=annee)
    eleve = inscription.eleve
    classe = inscription.classe
    
    cycles = CycleConfig.objects.filter(annee_scolaire=annee).order_by('date_debut')
    
    if classe:
        matieres = Matiere.objects.filter(
            enseignements__classe=classe,
            enseignements__classe__annee_scolaire=annee
        ).distinct()
    else:
            matieres = []
    
    cycles_data = []
    recap_data = []
    total_coef = 0
    total_moy_coef = 0
    
    from eleves.models import PeriodeCloture
    
    for cycle in cycles:
        p1_cloture = PeriodeCloture.objects.filter(classe=classe, periode=1).exists() if classe else False
        p2_cloture = PeriodeCloture.objects.filter(classe=classe, periode=2).exists() if classe else False
        
        def get_periode_from_cycle(cycle_numero):
            if cycle_numero == 1:
                return [1]
            elif cycle_numero == 2:
                if not p1_cloture:
                    return []  # Empty until P1 is clotured
                return [2]
            elif cycle_numero == 3:
                if not p1_cloture:
                    return []  # Empty until P1 is clotured
                if not p2_cloture:
                    return []  # Empty until P2 is clotured
                return [3]
            return [cycle_numero]
        
        periodes_to_show = get_periode_from_cycle(cycle.numero)
        
        matieres_data = []
        cycle_total_coef = 0
        cycle_total_moy_coef = 0
        
        for matiere in matieres:
            evals = Evaluation.objects.filter(
                eleve=eleve,
                matiere=matiere,
                annee_scolaire=annee,
                periode__in=periodes_to_show
            )
            
            grouped = {
                'interrogation': list(evals.filter(type_eval='interrogation')),
                'mini_devoir': list(evals.filter(type_eval='mini_devoir')),
                'devoir': list(evals.filter(type_eval='devoir')),
                'examen': list(evals.filter(type_eval='examen')),
            }
            
            type_avgs = []
            for evals_type in grouped.values():
                if evals_type:
                    avg = sum(float(e.note) for e in evals_type) / len(evals_type)
                    type_avgs.append(round(avg, 2))
            
            coef = float(matiere.coefficient or 1)
            
            if type_avgs:
                moyenne_sur_20 = round(sum(type_avgs) / len(type_avgs), 2)
                moyenne_coef = round(moyenne_sur_20 * coef, 2)
            else:
                moyenne_sur_20 = None
                moyenne_coef = None
            
            fiche = FicheNote.objects.filter(
                eleve=eleve, matiere=matiere, cycle=cycle
            ).first()
            
            matieres_data.append({
                'matiere': matiere,
                'fiche': fiche,
                'moyenne_sur_20': moyenne_sur_20,
                'moyenne_coef': moyenne_coef,
                'coefficient': coef,
                'grouped_evals': grouped,
                'interrogation_avg': round(sum(e.note for e in grouped['interrogation']) / len(grouped['interrogation']), 2) if grouped['interrogation'] else None,
                'mini_devoir_avg': round(sum(e.note for e in grouped['mini_devoir']) / len(grouped['mini_devoir']), 2) if grouped['mini_devoir'] else None,
                'devoir_avg': round(sum(e.note for e in grouped['devoir']) / len(grouped['devoir']), 2) if grouped['devoir'] else None,
                'examen_avg': round(sum(e.note for e in grouped['examen']) / len(grouped['examen']), 2) if grouped['examen'] else None,
            })
            
            if moyenne_sur_20 is not None:
                recap_data.append({
                    'matiere': matiere,
                    'cycle': cycle.libelle,
                    'cycle_pk': cycle.pk,
                    'coefficient': coef,
                    'moyenne_sur_20': moyenne_sur_20,
                    'moyenne_coef': moyenne_coef,
                    'rang': fiche.rang if fiche else None,
                })
                cycle_total_coef += coef
                cycle_total_moy_coef += moyenne_coef
                total_coef += coef
                total_moy_coef += moyenne_coef
        
        # Add conduite note for this cycle ONLY if periodes are clotured
        if periodes_to_show:
            from eleves.models import DisciplineEleve, ConduiteConfig
            note_base = 20
            config = ConduiteConfig.objects.filter(
                annee_scolaire=annee,
                niveau=classe.niveau
            ).first()
            if config:
                note_base = float(config.note_base)
            
            disciplines = DisciplineEleve.objects.filter(
                inscription=inscription,
                periode__in=periodes_to_show,
                statut_traitement='traite'
            )
            total_points_discipline = sum(d.points for d in disciplines)
            note_conduite = max(0, min(20, note_base + total_points_discipline))
            
            matieres_data.append({
                'matiere': None,
                'fiche': None,
                'moyenne_sur_20': note_conduite,
                'moyenne_coef': note_conduite * 1,
                'coefficient': 1,
                'grouped_evals': {},
                'is_conduite': True,
            })
            
            cycle_total_coef += 1
            cycle_total_moy_coef += note_conduite
            total_coef += 1
            total_moy_coef += note_conduite
        
        cycle_moyenne = round(cycle_total_moy_coef / cycle_total_coef, 2) if cycle_total_coef > 0 and cycle_total_moy_coef > 0 else None
        
        cycles_data.append({
            'cycle': cycle,
            'matieres': matieres_data,
            'total_coef': cycle_total_coef,
            'total_moy_coef': cycle_total_moy_coef,
            'moyenne_cycle': cycle_moyenne,
            'note_conduite': note_conduite if periodes_to_show else None,
        })
    
    moyenne_generale = round(total_moy_coef / total_coef, 2) if total_coef > 0 and total_moy_coef > 0 else None
    
    return render(request, 'academics/fiche_note_eleve.html', {
        'eleve': eleve,
        'classe': classe,
        'annee': annee,
        'inscription': inscription,
        'cycles_data': cycles_data,
        'matieres': matieres,
        'moyenne_generale': moyenne_generale,
        'grand_total_coef': total_coef,
        'grand_total_moy_coef': total_moy_coef,
        'recap_data': recap_data,
    })


@login_required
def bulletin_eleve_view(request, eleve_pk):
    from eleves.models import Inscription
    from finances.models import AnneeScolaire, CycleConfig
    from academics.models import Evaluation, FicheNote
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        return render(request, 'academics/bulletin.html', {
            'eleve': None, 'classe': None, 'annee': None,
            'cycles_data': [], 'recap_data': [], 'moyenne_generale': None,
            'grand_total_coef': 0, 'grand_total_moy_coef': 0,
        })
    
    inscription = get_object_or_404(Inscription, eleve_id=eleve_pk, annee_scolaire=annee)
    eleve = inscription.eleve
    classe = inscription.classe
    
    cycles = CycleConfig.objects.filter(annee_scolaire=annee).order_by('date_debut')
    
    if classe:
        matieres = Matiere.objects.filter(
            enseignements__classe=classe,
            enseignements__classe__annee_scolaire=annee
        ).distinct()
    else:
            matieres = []
    
    cycles_data = []
    recap_data = []
    total_coef = 0
    total_moy_coef = 0
    
    from eleves.models import PeriodeCloture
    
    for cycle in cycles:
        p1_cloture = PeriodeCloture.objects.filter(classe=classe, periode=1).exists() if classe else False
        p2_cloture = PeriodeCloture.objects.filter(classe=classe, periode=2).exists() if classe else False
        
        def get_periode_from_cycle(cycle_numero):
            if cycle_numero == 1:
                return [1]
            elif cycle_numero == 2:
                if not p1_cloture:
                    return []  # Empty until P1 is clotured
                return [2]
            elif cycle_numero == 3:
                if not p1_cloture:
                    return []  # Empty until P1 is clotured
                if not p2_cloture:
                    return []  # Empty until P2 is clotured
                return [3]
            return [cycle_numero]
        
        periodes_to_show = get_periode_from_cycle(cycle.numero)
        
        matieres_data = []
        cycle_total_coef = 0
        cycle_total_moy_coef = 0
        
        for matiere in matieres:
            evals = Evaluation.objects.filter(
                eleve=eleve,
                matiere=matiere,
                annee_scolaire=annee,
                periode__in=periodes_to_show
            )
            
            grouped = {
                'interrogation': list(evals.filter(type_eval='interrogation')),
                'mini_devoir': list(evals.filter(type_eval='mini_devoir')),
                'devoir': list(evals.filter(type_eval='devoir')),
                'examen': list(evals.filter(type_eval='examen')),
            }
            
            type_avgs = []
            for evals_type in grouped.values():
                if evals_type:
                    avg = sum(float(e.note) for e in evals_type) / len(evals_type)
                    type_avgs.append(round(avg, 2))
            
            coef = float(matiere.coefficient or 1)
            
            if type_avgs:
                moyenne_sur_20 = round(sum(type_avgs) / len(type_avgs), 2)
                moyenne_coef = round(moyenne_sur_20 * coef, 2)
            else:
                moyenne_sur_20 = None
                moyenne_coef = None
            
            fiche = FicheNote.objects.filter(
                eleve=eleve, matiere=matiere, cycle=cycle
            ).first()
            
            matieres_data.append({
                'matiere': matiere,
                'fiche': fiche,
                'moyenne_sur_20': moyenne_sur_20,
                'moyenne_coef': moyenne_coef,
                'coefficient': coef,
                'grouped_evals': grouped,
                'interrogation_avg': round(sum(e.note for e in grouped['interrogation']) / len(grouped['interrogation']), 2) if grouped['interrogation'] else None,
                'mini_devoir_avg': round(sum(e.note for e in grouped['mini_devoir']) / len(grouped['mini_devoir']), 2) if grouped['mini_devoir'] else None,
                'devoir_avg': round(sum(e.note for e in grouped['devoir']) / len(grouped['devoir']), 2) if grouped['devoir'] else None,
                'examen_avg': round(sum(e.note for e in grouped['examen']) / len(grouped['examen']), 2) if grouped['examen'] else None,
            })
            
            if moyenne_sur_20 is not None:
                recap_data.append({
                    'matiere': matiere,
                    'cycle': cycle.libelle,
                    'cycle_pk': cycle.pk,
                    'coefficient': coef,
                    'moyenne_sur_20': moyenne_sur_20,
                    'moyenne_coef': moyenne_coef,
                    'rang': fiche.rang if fiche else None,
                })
            
            if moyenne_sur_20 is not None:
                cycle_total_coef += coef
                cycle_total_moy_coef += moyenne_coef
                total_coef += coef
                total_moy_coef += moyenne_coef
        
        # Add conduite note for this cycle ONLY if periodes are clotured
        if periodes_to_show:
            from eleves.models import DisciplineEleve, ConduiteConfig
            note_base = 20
            config = ConduiteConfig.objects.filter(
                annee_scolaire=annee,
                niveau=classe.niveau
            ).first()
            if config:
                note_base = float(config.note_base)
            
            disciplines = DisciplineEleve.objects.filter(
                inscription=inscription,
                periode__in=periodes_to_show,
                statut_traitement='traite'
            )
            total_points_discipline = sum(d.points for d in disciplines)
            note_conduite = max(0, min(20, note_base + total_points_discipline))
            
            matieres_data.append({
                'matiere': None,
                'fiche': None,
                'moyenne_sur_20': note_conduite,
                'moyenne_coef': note_conduite * 1,
                'coefficient': 1,
                'grouped_evals': {},
                'is_conduite': True,
            })
            
            cycle_total_coef += 1
            cycle_total_moy_coef += note_conduite
            total_coef += 1
            total_moy_coef += note_conduite
        
        cycle_moyenne = round(cycle_total_moy_coef / cycle_total_coef, 2) if cycle_total_coef > 0 and cycle_total_moy_coef > 0 else None
        
        cycles_data.append({
            'cycle': cycle,
            'matieres_data': matieres_data,
            'total_coef': cycle_total_coef,
            'total_moy_coef': cycle_total_moy_coef,
            'moyenne_cycle': cycle_moyenne,
            'note_conduite': note_conduite if periodes_to_show else None,
        })
    
    moyenne_generale = round(total_moy_coef / total_coef, 2) if total_coef > 0 and total_moy_coef > 0 else None
    
    return render(request, 'academics/bulletin.html', {
        'eleve': eleve,
        'classe': classe,
        'annee': annee,
        'inscription': inscription,
        'cycles_data': cycles_data,
        'matieres': matieres,
        'moyenne_generale': moyenne_generale,
        'grand_total_coef': total_coef,
        'grand_total_moy_coef': total_moy_coef,
        'recap_data': recap_data,
    })


@login_required
def fiche_note_detail_view(request, eleve_pk, cycle_pk, matiere_pk):
    from eleves.models import Inscription
    from finances.models import AnneeScolaire, CycleConfig
    from academics.models import Evaluation, FicheNote
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    inscription = get_object_or_404(Inscription, eleve_id=eleve_pk, annee_scolaire=annee)
    eleve = inscription.eleve
    classe = inscription.classe
    matiere = get_object_or_404(Matiere, pk=matiere_pk)
    cycle = get_object_or_404(CycleConfig, pk=cycle_pk, annee_scolaire=annee)
    
    if request.method == 'POST':
        appreciation = request.POST.get('appreciation', '')
        fiche, _ = FicheNote.objects.update_or_create(
            eleve=eleve, matiere=matiere, cycle=cycle,
            defaults={'appreciation': appreciation}
        )
        messages.success(request, 'Appréciation enregistrée.')
        return redirect('academics:fiche_note_detail', eleve_pk=eleve.pk, cycle_pk=cycle.pk, matiere_pk=matiere.pk)
    
    evaluations = Evaluation.objects.filter(
        eleve=eleve,
        matiere=matiere,
        annee_scolaire=annee,
        date_eval__gte=cycle.date_debut,
        date_eval__lte=cycle.date_fin
    ).order_by('date_eval')
    
    grouped_evals = {
        'interrogation': evaluations.filter(type_eval='interrogation'),
        'mini_devoir': evaluations.filter(type_eval='mini_devoir'),
        'devoir': evaluations.filter(type_eval='devoir'),
        'examen': evaluations.filter(type_eval='examen'),
    }
    
    coef = float(matiere.coefficient or 1)
    
    type_avgs = []
    for evals_type in grouped_evals.values():
        if evals_type.exists():
            avg = evals_type.aggregate(avg=Avg('note'))['avg']
            type_avgs.append(float(avg))
    
    if type_avgs:
        moyenne_sur_20 = round(sum(type_avgs) / len(type_avgs), 2)
        moyenne_coef = round(moyenne_sur_20 * coef, 2)
    else:
                moyenne_sur_20 = None
                moyenne_coef = None
    
    fiche = FicheNote.objects.filter(eleve=eleve, matiere=matiere, cycle=cycle).first()
    
    return render(request, 'academics/fiche_note_detail.html', {
        'eleve': eleve,
        'classe': classe,
        'annee': annee,
        'inscription': inscription,
        'cycle': cycle,
        'matiere': matiere,
        'evaluations': evaluations,
        'grouped_evals': grouped_evals,
        'fiche': fiche,
        'moyenne_sur_20': moyenne_sur_20,
        'moyenne_coef': moyenne_coef,
        'coefficient': coef,
    })


@login_required
def classe_list(request):
    from eleves.models import Inscription
    from finances.models import AnneeScolaire, CycleConfig
    from academics.models import Evaluation
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        return render(request, 'academics/classe_fiche_notes.html', {
            'classe': None,
            'eleves': [],
            'eleves_data': [],
            'matieres': [],
            'cycles': [],
            'selected_matiere': None,
            'annee': None,
        })
    
    classe = get_object_or_404(Classe, pk=classe_pk)
    
    eleves = Inscription.objects.filter(
        classe=classe,
        annee_scolaire=annee
    ).select_related('eleve')
    
    matieres = Matiere.objects.filter(
        enseignements__classe=classe,
        enseignements__classe__annee_scolaire=annee
    ).distinct()
    
    cycles = CycleConfig.objects.filter(
        annee_scolaire=annee
    ).order_by('date_debut')
    
    cycle = None
    if cycle_pk:
        cycle = get_object_or_404(CycleConfig, pk=cycle_pk)
    elif cycles.exists():
        cycle = cycles.first()
    
    selected_matiere_id = request.GET.get('matiere')
    selected_matiere = None
    if selected_matiere_id:
        selected_matiere = get_object_or_404(Matiere, pk=selected_matiere_id)
    
    eleves_data = []
    for inscription in eleves:
        eleve_data = {
            'inscription': inscription,
            'eleve': inscription.eleve,
            'matieres': []
        }
        
        matieres_to_show = [selected_matiere] if selected_matiere else list(matieres)
        
        for matiere in matieres_to_show:
            matiere_data = {
                'matiere': matiere,
                'evaluations': {},
                'moyenne_sur_20': None,
                'moyenne_coef': None
            }
            
            evals = Evaluation.objects.filter(
                eleve=inscription.eleve,
                matiere=matiere,
                annee_scolaire=annee
            ).order_by('date_eval')
            
            interp_notes = []
            mini_devoir_notes = []
            devoir_notes = []
            
            for e in evals:
                if e.type_eval == 'interrogation':
                    interp_notes.append(e.note)
                elif e.type_eval == 'mini_devoir':
                    mini_devoir_notes.append(e.note)
                elif e.type_eval == 'devoir':
                    devoir_notes.append(e.note)
            
            def calc_moy(notes):
                if notes:
                    return round(sum(notes) / len(notes), 2)
                return None
            
            matiere_data['evaluations'] = {
                'interrogation': {'notes': interp_notes, 'moyenne': calc_moy(interp_notes)},
                'mini_devoir': {'notes': mini_devoir_notes, 'moyenne': calc_moy(mini_devoir_notes)},
                'devoir': {'notes': devoir_notes, 'moyenne': calc_moy(devoir_notes)},
            }
            
            all_notes = interp_notes + mini_devoir_notes + devoir_notes
            if all_notes:
                moy = calc_moy(all_notes)
                matiere_data['moyenne_sur_20'] = moy
                matiere_data['moyenne_coef'] = round(moy * matiere.coefficient, 2) if moy else None
            
            eleve_data['matieres'].append(matiere_data)
        
        total_coef = sum(m.coefficient for m in matieres)
        total_moy_coef = sum(
            (m.get('moyenne_sur_20', 0) or 0) * m.get('matiere', {}).coefficient 
            for m in eleve_data['matieres'] if m.get('moyenne_sur_20')
        )
        eleve_data['moyenne_generale'] = round(total_moy_coef / total_coef, 2) if total_coef > 0 else None
        
        eleves_data.append(eleve_data)
    
    eleves_data.sort(key=lambda x: x['moyenne_generale'] or 0, reverse=True)
    for i, data in enumerate(eleves_data):
        data['rang'] = i + 1
        if data['moyenne_generale']:
            if data['moyenne_generale'] >= 18:
                data['mention'] = 'EXCELLENT'
            elif data['moyenne_generale'] >= 16:
                data['mention'] = 'TRES_BIEN'
            elif data['moyenne_generale'] >= 14:
                data['mention'] = 'BIEN'
            elif data['moyenne_generale'] >= 12:
                data['mention'] = 'ASSEZ_BIEN'
            elif data['moyenne_generale'] >= 10:
                data['mention'] = 'PASSABLE'
            else:
                data['mention'] = 'INSUFFISANT'
        else:
            data['mention'] = None
    
    matieres_with_data = []
    if matieres:
        matieres_with_data = [
            {'matiere': m, 'coefficient': m.coefficient}
            for m in matieres
        ]
    
    return render(request, 'academics/classe_fiche_notes.html', {
        'classe': classe,
        'eleves': eleves,
        'eleves_data': eleves_data,
        'matieres': matieres,
        'matieres_with_data': matieres_with_data,
        'cycles': cycles,
        'cycle': cycle,
        'selected_matiere': selected_matiere,
        'annee': annee,
    })


@login_required
def view_func(request):
    from finances.models import AnneeScolaire
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
    
    schedule = {jour: [] for jour in jours}
    
    if hasattr(request.user, 'professeur') and request.user.professeur:
        enseignements = Enseignement.objects.filter(
            professeur=request.user.professeur,
            classe__annee_scolaire=annee
        ).select_related('classe', 'matiere', 'professeur')
    else:
            enseignements = Enseignement.objects.filter(
    classe__annee_scolaire=annee
    ).select_related('professeur', 'classe', 'matiere')
    
    for ens in enseignements:
        if ens.horaires:
            for h in ens.horaires:
                jour = h.get('jour', '').lower()
                if jour in schedule:
                    schedule[jour].append({
                        'heure_debut': h.get('heure_debut'),
                        'heure_fin': h.get('heure_fin'),
                        'matiere': ens.matiere,
                        'classe': ens.classe,
                        'professeur': ens.professeur
                    })
    
    for jour in schedule:
        schedule[jour].sort(key=lambda x: x['heure_debut'] or '')
    
    return render(request, 'academics/emploi_du_temps.html', {
        'schedule': schedule,
        'jours': jours,
        'annee': annee
    })


@login_required
def emploi_du_temps_view(request):
    if not request.user.has_module_permission('emploi_du_temps', 'read'):
            messages.error(request, "Vous n'avez pas l'autorisation de voir l'emploi du temps.")
            return redirect('dashboard')
    
    from finances.models import AnneeScolaire
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
    classes = Classe.objects.filter(annee_scolaire=annee).order_by('niveau', 'nom')
    professeurs = Professeur.objects.all().order_by('nom', 'prenom')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'ajouter':
            prof_id = request.POST.get('professeur')
            classe_id = request.POST.get('classe')
            matiere_id = request.POST.get('matiere')
            jour = request.POST.get('jour')
            heure_debut = request.POST.get('heure_debut')
            heure_fin = request.POST.get('heure_fin')
            
            if prof_id and classe_id and matiere_id and jour and heure_debut and heure_fin:
                ens = Enseignement.objects.filter(
                    professeur_id=prof_id,
                    classe_id=classe_id,
                    matiere_id=matiere_id
                ).first()
                
                if ens:
                    horaires = ens.horaires or []
                    horaires.append({
                        'jour': jour,
                        'heure_debut': heure_debut,
                        'heure_fin': heure_fin
                    })
                    ens.horaires = horaires
                    ens.save()
                    messages.success(request, "Horaire ajouté avec succès.")
                else:
                    messages.error(request, "Attribution non trouvée. Veuillez créer d'abord l'attribution.")
        elif action == 'supprimer':
            ens_id = request.POST.get('ens_id')
            jour = request.POST.get('jour')
            heure_debut = request.POST.get('heure_debut')
            heure_fin = request.POST.get('heure_fin')
            
            if ens_id:
                ens = Enseignement.objects.get(pk=ens_id)
                if ens.horaires:
                    new_horaires = [h for h in ens.horaires if not (
                        h.get('jour') == jour and 
                        h.get('heure_debut') == heure_debut and 
                        h.get('heure_fin') == heure_fin
                    )]
                    ens.horaires = new_horaires
                    ens.save()
                    messages.success(request, "Horaire supprimé.")
                    return redirect('academics:emploi_du_temps')
    
    enseignements = Enseignement.objects.filter(
        classe__annee_scolaire=annee
    ).select_related('professeur', 'classe', 'matiere')
    
    schedule_grid = {jour: {} for jour in jours}
    schedule_by_prof = {}
    time_slots_set = set()
    
    for ens in enseignements:
        if ens.horaires:
            for h in ens.horaires:
                jour = h.get('jour', '').lower()
                debut = h.get('heure_debut', '')
                fin = h.get('heure_fin', '')
                
                if jour in schedule_grid and debut and fin:
                    if debut not in schedule_grid[jour]:
                        schedule_grid[jour][debut] = []
                    schedule_grid[jour][debut].append({
                        'ens': ens,
                        'jour': jour,
                        'heure_debut': debut,
                        'heure_fin': fin
                    })
                    time_slots_set.add(debut)
                    
                    key = (ens.professeur, ens.pk, jour, debut, fin)
                    if ens.professeur not in schedule_by_prof:
                        schedule_by_prof[ens.professeur] = []
                    schedule_by_prof[ens.professeur].append({
                        'jour': jour,
                        'heure_debut': debut,
                        'heure_fin': fin,
                        'classe': ens.classe,
                        'matiere': ens.matiere,
                        'pk': ens.pk
                    })
    
    time_slots = sorted(time_slots_set)
    
    return render(request, 'academics/emploi_du_temps_list.html', {
        'annee': annee,
        'professeurs': professeurs,
        'classes': classes,
        'jours': jours,
        'time_slots': time_slots,
        'schedule_grid': schedule_grid,
        'schedule_by_prof': schedule_by_prof,
    })


@login_required
def emploi_du_temps_reset_view(request):
    if not request.user.has_module_permission('emploi_du_temps', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de réinitialiser l'emploi du temps.")
        return redirect('academics:emploi_du_temps')
    
    messages.info(request, "Fonctionnalite en cours de developpement.")
    return redirect('academics:emploi_du_temps')


@login_required
def salle_list_view(request):
    if not request.user.has_module_permission('salle_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les salles.")
        return redirect('dashboard')
    
    salles = Salle.objects.all().order_by('nom')
    return render(request, 'academics/salle_list.html', {'salles': salles})


@login_required
def salle_create_view(request):
    if not request.user.has_module_permission('salle_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des salles.")
        return redirect('academics:salle_list')
    
    if request.method == 'POST':
        form = SalleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salle creee avec succes.')
            return redirect('academics:salle_list')
    else:
        form = SalleForm()
    return render(request, 'academics/salle_form.html', {'form': form})


@login_required
def salle_edit_view(request, pk):
    if not request.user.has_module_permission('salle_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des salles.")
        return redirect('academics:salle_list')
    
    salle = get_object_or_404(Salle, pk=pk)
    if request.method == 'POST':
        form = SalleForm(request.POST, instance=salle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salle modifiee avec succes.')
            return redirect('academics:salle_list')
    else:
        form = SalleForm(instance=salle)
    return render(request, 'academics/salle_form.html', {'form': form})


@login_required
def salle_delete_view(request, pk):
    if not request.user.has_module_permission('salle_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des salles.")
        return redirect('academics:salle_list')
    
    salle = get_object_or_404(Salle, pk=pk)
    if request.method == 'POST':
        salle.delete()
        messages.success(request, 'Salle supprimee avec succes.')
        return redirect('academics:salle_list')
    return render(request, 'academics/salle_confirm_delete.html', {'salle': salle})


@login_required
def coefficient_list_view(request):
    if not request.user.has_module_permission('classe_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les coefficients.")
        return redirect('dashboard')
    
    coefficients = CoefficientMatiere.objects.all().select_related('classe', 'matiere')
    return render(request, 'academics/coefficient_list.html', {'coefficients': coefficients})


@login_required
def coefficient_create_view(request):
    if not request.user.has_module_permission('classe_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de créer des coefficients.")
        return redirect('academics:coefficient_list')
    
    if request.method == 'POST':
        form = CoefficientMatiereForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coefficient cree avec succes.')
            return redirect('academics:coefficient_list')
    else:
        form = CoefficientMatiereForm()
    return render(request, 'academics/coefficient_form.html', {'form': form})


@login_required
def coefficient_edit_view(request, pk):
    if not request.user.has_module_permission('classe_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des coefficients.")
        return redirect('academics:coefficient_list')
    
    coefficient = get_object_or_404(CoefficientMatiere, pk=pk)
    if request.method == 'POST':
        form = CoefficientMatiereForm(request.POST, instance=coefficient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coefficient modifie avec succes.')
            return redirect('academics:coefficient_list')
    else:
        form = CoefficientMatiereForm(instance=coefficient)
    return render(request, 'academics/coefficient_form.html', {'form': form})


@login_required
def coefficient_delete_view(request, pk):
    coefficient = get_object_or_404(CoefficientMatiere, pk=pk)
    if request.method == 'POST':
        if not request.user.has_module_permission('classe_list', 'delete'):
            messages.error(request, "Vous n'avez pas l'autorisation de supprimer des coefficients.")
            return redirect('academics:coefficient_list')
        coefficient.delete()
        messages.success(request, 'Coefficient supprime avec succes.')
        return redirect('academics:coefficient_list')
    return render(request, 'academics/coefficient_confirm_delete.html', {'coefficient': coefficient})


@login_required
def examen_list_view(request):
    if not request.user.has_module_permission('examen_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les examens.")
        return redirect('dashboard')
    
    examens = Examen.objects.all().order_by('-date_examen')
    return render(request, 'academics/examen_list.html', {'examens': examens})


@login_required
def examen_create_view(request):
    if not request.user.has_module_permission('examen_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des examens.")
        return redirect('academics:examen_list')
    
    if request.method == 'POST':
        form = ExamenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Examen cree avec succes.')
            return redirect('academics:examen_list')
    else:
        form = ExamenForm()
    return render(request, 'academics/examen_form.html', {'form': form})


@login_required
def examen_edit_view(request, pk):
    if not request.user.has_module_permission('examen_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des examens.")
        return redirect('academics:examen_list')
    
    examen = get_object_or_404(Examen, pk=pk)
    if request.method == 'POST':
        form = ExamenForm(request.POST, instance=examen)
        if form.is_valid():
            form.save()
            messages.success(request, 'Examen modifie avec succes.')
            return redirect('academics:examen_list')
    else:
        form = ExamenForm(instance=examen)
    return render(request, 'academics/examen_form.html', {'form': form, 'examen': examen})


@login_required
def examen_detail_view(request, pk):
    examen = get_object_or_404(Examen, pk=pk)
    return render(request, 'academics/examen_detail.html', {'examen': examen, 'epreuves': []})


@login_required
def examen_delete_view(request, pk):
    if not request.user.has_module_permission('examen_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des examens.")
        return redirect('academics:examen_list')
    
    examen = get_object_or_404(Examen, pk=pk)
    if request.method == 'POST':
        examen.delete()
        messages.success(request, 'Examen supprime avec succes.')
        return redirect('academics:examen_list')
    return render(request, 'academics/examen_confirm_delete.html', {'examen': examen})


@login_required
def examen_publish_view(request, pk):
    examen = get_object_or_404(Examen, pk=pk)
    examen.publie = True
    examen.save()
    messages.success(request, 'Examen publie avec succes.')
    return redirect('academics:examen_list')


@login_required
def examen_schedule_view(request):
    messages.info(request, "Fonctionnalite en cours de developpement.")
    return redirect('academics:examen_list')


@login_required
def contrainte_list_view(request):
    contraintes = ContrainteHoraire.objects.all().select_related('professeur')
    return render(request, 'academics/contrainte_list.html', {'contraintes': contraintes})


@login_required
def contrainte_create_view(request):
    from authentification.models import DemandeApprobation, User
    
    is_direction = request.user.is_direction() or request.user.is_superadmin()
    
    if request.method == 'POST':
        form = ContrainteHoraireForm(request.POST)
        if form.is_valid():
            contrainte = form.save(commit=False)
            
            attributions = Enseignement.objects.filter(
                professeur=contrainte.professeur,
                classe__annee_scolaire__est_active=True
            )
            
            conflits = []
            for att in attributions:
                if att.horaires:
                    for h in att.horaires:
                        if h.get('jour') == contrainte.jour:
                            h_debut = h.get('heure_debut', '')
                            h_fin = h.get('heure_fin', '')
                            if h_debut and h_fin and contrainte.heure_debut and contrainte.heure_fin:
                                if not (h_fin <= contrainte.heure_debut.strftime('%H:%M') or h_debut >= contrainte.heure_fin.strftime('%H:%M')):
                                    conflits.append(f"{att.classe.nom} - {att.matiere.nom} ({h.get('jour', '').capitalize()} {h_debut}-{h_fin})")
            
            if not is_direction:
                details_apos = f"""Demande de {contrainte.get_type_contrainte_display()}:
- Jour: {contrainte.get_jour_display()}
- Heure de début: {contrainte.heure_debut.strftime('%H:%M')}
- Heure de fin: {contrainte.heure_fin.strftime('%H:%M')}
- Type: {contrainte.get_type_contrainte_display()}
- Motif: {contrainte.motif or 'Non spécifié'}
- Récurrent: {'Oui' if contrainte.est_recurrent else 'Non'}
- Date fin: {contrainte.date_fin or 'Non définie'}"""
                
                demande = DemandeApprobation.objects.create(
                    demandeur=request.user,
                    type_action=DemandeApprobation.TypeAction.CREATION,
                    type_objet=DemandeApprobation.TypeObjet.CONTRAINTE,
                    objet_repr=f"{contrainte.professeur} - {contrainte.get_jour_display()} {contrainte.heure_debut}-{contrainte.heure_fin}",
                    details=f"Demande de {contrainte.get_type_contrainte_display()} pour {contrainte.professeur}",
                    details_apos=details_apos
                )
                
                contrainte.statut = ContrainteHoraire.Statut.EN_ATTENTE
                contrainte.save()
                demande.objet_id = contrainte.pk
                demande.save()
                
                approbateurs = User.objects.filter(role__in=[User.Role.SUPERADMIN, User.Role.DIRECTION], is_active=True)
                from authentification.models import Notification
                for approbateur in approbateurs:
                    Notification.creer_notification(
                        destinataire=approbateur,
                        type_notification=Notification.TypeNotification.AUTRE,
                        titre=f"Demande de {contrainte.get_type_contrainte_display()}",
                        message=f"{request.user.get_full_name() or request.user.username} demande {contrainte.get_type_contrainte_display().lower()} pour le {contrainte.get_jour_display()} {contrainte.heure_debut}-{contrainte.heure_fin}",
                        expediteur=request.user,
                        lien='/accounts/demandes/'
                    )
                
                messages.success(request, 'Votre demande a été soumise pour approbation.')
                return redirect('academics:contrainte_list')
            
            if conflits:
                messages.warning(request, f"Attention: Cette contrainte entre en conflit avec les attributions existantes: {', '.join(conflits)}. Vous pouvez continuer, mais attention aux doublons d'horaires.")
            
            contrainte.statut = ContrainteHoraire.Statut.APPROUVE
            contrainte.save()
            messages.success(request, 'Contrainte créée avec succès.')
            return redirect('academics:contrainte_list')
    else:
        if hasattr(request.user, 'professeur') and request.user.professeur:
            form = ContrainteHoraireForm(initial={'professeur': request.user.professeur})
        else:
            form = ContrainteHoraireForm()
    return render(request, 'academics/contrainte_form.html', {'form': form})


@login_required
def contrainte_edit_view(request, pk):
    if not request.user.has_module_permission('contrainte_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des contraintes.")
        return redirect('academics:contrainte_list')
    
    contrainte = get_object_or_404(ContrainteHoraire, pk=pk)
    if request.method == 'POST':
        form = ContrainteHoraireForm(request.POST, instance=contrainte)
        if form.is_valid():
            contrainte_updated = form.save(commit=False)
            
            attributions = Enseignement.objects.filter(
                professeur=contrainte_updated.professeur,
                classe__annee_scolaire__est_active=True
            )
            
            conflits = []
            for att in attributions:
                if att.horaires:
                    for h in att.horaires:
                        if h.get('jour') == contrainte_updated.jour:
                            h_debut = h.get('heure_debut', '')
                            h_fin = h.get('heure_fin', '')
                            if h_debut and h_fin and contrainte_updated.heure_debut and contrainte_updated.heure_fin:
                                if not (h_fin <= contrainte_updated.heure_debut.strftime('%H:%M') or h_debut >= contrainte_updated.heure_fin.strftime('%H:%M')):
                                    conflits.append(f"{att.classe.nom} - {att.matiere.nom} ({h.get('jour', '').capitalize()} {h_debut}-{h_fin})")
            
            if conflits:
                messages.warning(request, f"Attention: Cette contrainte entre en conflit avec les attributions existantes: {', '.join(conflits)}.")
            
            contrainte_updated.save()
            messages.success(request, 'Contrainte modifiee avec succes.')
            return redirect('academics:contrainte_list')
    else:
        form = ContrainteHoraireForm(instance=contrainte)
    return render(request, 'academics/contrainte_form.html', {'form': form})


@login_required
def contrainte_delete_view(request, pk):
    if not request.user.has_module_permission('contrainte_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des contraintes.")
        return redirect('academics:contrainte_list')
    
    contrainte = get_object_or_404(ContrainteHoraire, pk=pk)
    if request.method == 'POST':
        contrainte.delete()
        messages.success(request, 'Contrainte supprimee avec succes.')
        return redirect('academics:contrainte_list')
    return render(request, 'academics/contrainte_confirm_delete.html', {'contrainte': contrainte})
