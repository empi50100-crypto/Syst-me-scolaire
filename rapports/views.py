from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Avg, Sum, Count, Q
from datetime import date
from eleves.models import Eleve, Inscription, DisciplineEleve
from academics.models import Classe, Matiere, Evaluation, FicheNote, Enseignement
from finances.models import AnneeScolaire, FraisScolaire, Paiement, CycleConfig
from presences.models import Presence
from .models import Bulletin


def calculer_total_frais_avec_eleves(annee):
    from eleves.models import Inscription
    from academics.models import Classe
    from django.db.models import Q
    
    total_frais = 0
    frais_list = FraisScolaire.objects.filter(
        Q(annee_scolaire=annee) | Q(annee_scolaire__isnull=True)
    )
    
    for frais in frais_list:
        classes_concernees = frais.get_classes_concernees()
        nb_eleves = Inscription.objects.filter(
            annee_scolaire=annee,
            classe__in=classes_concernees
        ).count()
        total_frais += float(frais.montant) * nb_eleves
    
    return total_frais


def calculer_moyenne_matiere(eleve, matiere, annee, cycle=None):
    from eleves.models import PeriodeCloture
    
    inscription = Inscription.objects.filter(eleve=eleve, annee_scolaire=annee).first()
    classe = inscription.classe if inscription else None
    
    p1_cloture = PeriodeCloture.objects.filter(classe=classe, periode=1).exists() if classe else False
    p2_cloture = PeriodeCloture.objects.filter(classe=classe, periode=2).exists() if classe else False
    
    def get_periode_from_cycle(cycle_numero):
        if cycle_numero == 1:
            return [1]
        elif cycle_numero == 2:
            if not p1_cloture:
                return []
            return [2]
        elif cycle_numero == 3:
            if not p1_cloture:
                return []
            if not p2_cloture:
                return []
            return [3]
        return [cycle_numero]
    
    if cycle:
        periodes = get_periode_from_cycle(cycle.numero)
        if not periodes:
            return None
        evaluations = Evaluation.objects.filter(
            eleve=eleve, 
            matiere=matiere, 
            annee_scolaire=annee,
            periode__in=periodes
        )
    else:
        evaluations = Evaluation.objects.filter(eleve=eleve, matiere=matiere, annee_scolaire=annee)
    
    if not evaluations.exists():
        fiche = FicheNote.objects.filter(eleve=eleve, matiere=matiere, cycle=cycle).first()
        if fiche and fiche.moyenne:
            return float(fiche.moyenne)
        return None
    
    total_points = sum(float(e.note) * e.coefficient for e in evaluations)
    total_coef = sum(e.coefficient for e in evaluations)
    
    return round(total_points / total_coef, 2) if total_coef > 0 else None


def calculer_note_conduite(eleve, classe, annee, cycle=None):
    from eleves.models import ConduiteConfig
    
    inscription = Inscription.objects.filter(eleve=eleve, annee_scolaire=annee, classe=classe).first()
    if not inscription:
        return None
    
    note_base = 20
    config = ConduiteConfig.objects.filter(
        annee_scolaire=annee,
        niveau=classe.niveau
    ).first()
    if config:
        note_base = float(config.note_base)
    
    periodes = [1, 2, 3]
    
    disciplines = DisciplineEleve.objects.filter(
        inscription=inscription,
        periode__in=periodes,
        statut_traitement='traite'
    )
    
    total_points = sum(d.points for d in disciplines)
    
    note_conduite = max(0, min(20, note_base + total_points))
    
    return note_conduite


def calculer_moyenne_generale(eleve, classe, annee, cycle=None):
    matieres = Matiere.objects.filter(
        enseignements__classe=classe,
        enseignements__classe__annee_scolaire=annee
    ).distinct()
    
    total_points = 0
    total_coef = 0
    
    for matiere in matieres:
        moyenne = calculer_moyenne_matiere(eleve, matiere, annee, cycle)
        if moyenne is not None:
            total_points += moyenne * matiere.coefficient
            total_coef += matiere.coefficient
    
    return round(total_points / total_coef, 2) if total_coef > 0 else None


def get_mention(moyenne):
    if moyenne is None:
        return ''
    elif moyenne >= 16:
        return 'Excellent'
    elif moyenne >= 14:
        return 'Très Bien'
    elif moyenne >= 12:
        return 'Bien'
    elif moyenne >= 10:
        return 'Assez Bien'
    elif moyenne >= 8:
        return 'Passable'
    else:
        return 'Insuffisant'


@login_required
def bulletin_list(request):
    if not request.user.has_module_permission('bulletins', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les bulletins.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    cycles = CycleConfig.objects.filter(annee_scolaire=annee).order_by('numero') if annee else []
    selected_cycle_pk = request.GET.get('cycle')
    selected_cycle = None
    if selected_cycle_pk:
        selected_cycle = get_object_or_404(CycleConfig, pk=selected_cycle_pk)
    elif cycles.exists():
        selected_cycle = cycles.first()
    
    classes = Classe.objects.filter(annee_scolaire=annee) if annee else []
    selected_classe_pk = request.GET.get('classe')
    selected_classe = None
    if selected_classe_pk:
        selected_classe = get_object_or_404(Classe, pk=selected_classe_pk)
    
    search = request.GET.get('search', '')
    
    inscriptions_data = []
    
    if not selected_classe and annee:
        inscriptions = Inscription.objects.filter(
            annee_scolaire=annee
        ).select_related('eleve', 'classe').order_by('classe__nom', 'eleve__nom')
        
        if search:
            inscriptions = inscriptions.filter(
                Q(eleve__nom__icontains=search) |
                Q(eleve__prenom__icontains=search) |
                Q(eleve__matricule__icontains=search)
            )
        
        from eleves.models import PeriodeCloture
        
        classes_with_inscriptions = set(inscriptions.values_list('classe_id', flat=True))
        
        cloture_by_class = {}
        for classe_id in classes_with_inscriptions:
            cloture_by_class[classe_id] = {
                'p1': PeriodeCloture.objects.filter(classe_id=classe_id, periode=1).exists(),
                'p2': PeriodeCloture.objects.filter(classe_id=classe_id, periode=2).exists(),
            }
        
        def get_periode_from_cycle_for_class(cycle_numero, p1_cloture, p2_cloture):
            if cycle_numero == 1:
                return [1]
            elif cycle_numero == 2:
                if not p1_cloture:
                    return []
                return [2]
            elif cycle_numero == 3:
                if not p1_cloture:
                    return []
                if not p2_cloture:
                    return []
                return [3]
            return [cycle_numero]
        
        for inscription in inscriptions:
            classe = inscription.classe
            clotures = cloture_by_class.get(classe.id, {'p1': False, 'p2': False})
            
            periodes = get_periode_from_cycle_for_class(
                selected_cycle.numero if selected_cycle else 1,
                clotures['p1'],
                clotures['p2']
            )
            
            total_points = 0
            total_coef = 0
            has_other_subject_notes = False
            
            matieres = Matiere.objects.filter(
                enseignements__classe=classe,
                enseignements__classe__annee_scolaire=annee
            ).distinct()
            
            for matiere in matieres:
                if selected_cycle and not periodes:
                    moyenne = None
                else:
                    evaluations = Evaluation.objects.filter(
                        eleve=inscription.eleve,
                        matiere=matiere,
                        annee_scolaire=annee,
                        periode__in=periodes if periodes else [1, 2, 3]
                    )
                    
                    if evaluations.exists():
                        total_points_matiere = sum(float(e.note) * e.coefficient for e in evaluations)
                        total_coef_matiere = sum(e.coefficient for e in evaluations)
                        moyenne = round(total_points_matiere / total_coef_matiere, 2) if total_coef_matiere > 0 else None
                    else:
                        moyenne = None
                
                if moyenne is not None:
                    has_other_subject_notes = True
                    total_points += moyenne * matiere.coefficient
                    total_coef += matiere.coefficient
            
            if has_other_subject_notes:
                from eleves.models import ConduiteConfig
                note_base = 20
                config = ConduiteConfig.objects.filter(
                    annee_scolaire=annee,
                    niveau=classe.niveau
                ).first()
                if config:
                    note_base = float(config.note_base)
                
                disciplines = DisciplineEleve.objects.filter(
                    inscription=inscription,
                    periode__in=periodes if periodes else [1, 2, 3],
                    statut_traitement='traite'
                )
                total_points_discipline = sum(d.points for d in disciplines)
                note_conduite = max(0, min(20, note_base + total_points_discipline))
                
                total_points += note_conduite * 1
                total_coef += 1
                moyenne_generale = round(total_points / total_coef, 2) if total_coef > 0 else None
            else:
                moyenne_generale = None
            
            inscriptions_data.append({
                'inscription': inscription,
                'moyenne_generale': moyenne_generale,
                'note_conduite': None,
                'cycle': selected_cycle,
            })
        
        inscriptions_data.sort(key=lambda x: x['moyenne_generale'] or 0, reverse=True)
    elif selected_classe:
        inscriptions = Inscription.objects.filter(
            classe=selected_classe, 
            annee_scolaire=annee
        ).select_related('eleve')
        
        if search:
            inscriptions = inscriptions.filter(
                Q(eleve__nom__icontains=search) |
                Q(eleve__prenom__icontains=search) |
                Q(eleve__matricule__icontains=search)
            )
        
        from eleves.models import PeriodeCloture
        
        p1_cloture = PeriodeCloture.objects.filter(classe=selected_classe, periode=1).exists()
        p2_cloture = PeriodeCloture.objects.filter(classe=selected_classe, periode=2).exists()
        
        def get_periode_from_cycle(cycle_numero):
            if cycle_numero == 1:
                return [1]
            elif cycle_numero == 2:
                if not p1_cloture:
                    return []
                return [2]
            elif cycle_numero == 3:
                if not p1_cloture:
                    return []
                if not p2_cloture:
                    return []
                return [3]
            return [cycle_numero]
        
        periodes = get_periode_from_cycle(selected_cycle.numero) if selected_cycle else [1, 2, 3]
        
        for inscription in inscriptions:
            total_points = 0
            total_coef = 0
            has_other_subject_notes = False
            
            matieres = Matiere.objects.filter(
                enseignements__classe=selected_classe,
                enseignements__classe__annee_scolaire=annee
            ).distinct()
            
            for matiere in matieres:
                if selected_cycle and not periodes:
                    moyenne = None
                else:
                    evaluations = Evaluation.objects.filter(
                        eleve=inscription.eleve,
                        matiere=matiere,
                        annee_scolaire=annee,
                        periode__in=periodes if periodes else [1, 2, 3]
                    )
                    
                    if evaluations.exists():
                        total_points_matiere = sum(float(e.note) * e.coefficient for e in evaluations)
                        total_coef_matiere = sum(e.coefficient for e in evaluations)
                        moyenne = round(total_points_matiere / total_coef_matiere, 2) if total_coef_matiere > 0 else None
                    else:
                        moyenne = None
                
                if moyenne is not None:
                    has_other_subject_notes = True
                    total_points += moyenne * matiere.coefficient
                    total_coef += matiere.coefficient
            
            if has_other_subject_notes:
                from eleves.models import ConduiteConfig
                note_base = 20
                config = ConduiteConfig.objects.filter(
                    annee_scolaire=annee,
                    niveau=selected_classe.niveau
                ).first()
                if config:
                    note_base = float(config.note_base)
                
                disciplines = DisciplineEleve.objects.filter(
                    inscription=inscription,
                    periode__in=periodes if periodes else [1, 2, 3],
                    statut_traitement='traite'
                )
                total_points_discipline = sum(d.points for d in disciplines)
                note_conduite = max(0, min(20, note_base + total_points_discipline))
                
                total_points += note_conduite * 1
                total_coef += 1
                moyenne_generale = round(total_points / total_coef, 2) if total_coef > 0 else None
            else:
                moyenne_generale = None
            
            inscriptions_data.append({
                'inscription': inscription,
                'moyenne_generale': moyenne_generale,
                'note_conduite': None,
                'cycle': selected_cycle,
            })
        
        inscriptions_data.sort(key=lambda x: x['moyenne_generale'] or 0, reverse=True)
        for i, data in enumerate(inscriptions_data, 1):
            data['rang'] = i
    
    bulletins = Bulletin.objects.select_related('eleve', 'inscription', 'cycle').order_by('-date_generation')
    
    if search:
        bulletins = bulletins.filter(
            eleve__nom__icontains=search
        ) | bulletins.filter(
            eleve__prenom__icontains=search
        ) | bulletins.filter(
            eleve__matricule__icontains=search
        )
    
    return render(request, 'rapports/bulletin_list.html', {
        'bulletins': bulletins,
        'inscriptions_data': inscriptions_data,
        'search': search,
        'classes': classes,
        'cycles': cycles,
        'selected_cycle': selected_cycle,
        'selected_classe': selected_classe,
    })


@login_required
def rapport_academique(request):
    if not request.user.has_module_permission('rapports', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les rapports.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    eleves_count = Eleve.objects.filter(statut='actif').count()
    inscriptions_count = Inscription.objects.filter(annee_scolaire=annee).count() if annee else 0
    
    classes_count = Classe.objects.filter(annee_scolaire=annee).count() if annee else 0
    
    presence_stats = {}
    if annee:
        total_presences = Presence.objects.filter(
            date__gte=annee.date_debut,
            date__lte=annee.date_fin
        ).count()
        
        presences_count = Presence.objects.filter(
            date__gte=annee.date_debut,
            date__lte=annee.date_fin,
            statut='present'
        ).count()
        
        taux_presence = (presences_count / total_presences * 100) if total_presences > 0 else 0
        presence_stats = {
            'total': total_presences,
            'presents': presences_count,
            'absents': total_presences - presences_count,
            'taux': round(taux_presence, 2)
        }
    
    return render(request, 'rapports/rapport_academique.html', {
        'annee': annee,
        'eleves_count': eleves_count,
        'inscriptions_count': inscriptions_count,
        'classes_count': classes_count,
        'presence_stats': presence_stats,
    })


@login_required
def rapport_financier(request):
    if not request.user.has_module_permission('rapports', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les rapports.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    total_frais = calculer_total_frais_avec_eleves(annee) if annee else 0
    total_paiements = Paiement.objects.filter(annee_scolaire=annee).aggregate(total=Sum('montant'))['total'] or 0
    
    frais_impayes = FraisScolaire.objects.filter(annee_scolaire=annee, statut='impaye')
    
    return render(request, 'rapports/rapport_financier.html', {
        'annee': annee,
        'total_frais': total_frais,
        'total_paiements': total_paiements,
        'frais_impayes': frais_impayes,
    })


@login_required
def transition_annee(request):
    if not request.user.has_module_permission('rapports', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    from django.db import transaction
    
    annee_actuelle = AnneeScolaire.objects.filter(est_active=True).first()
    
    if not annee_actuelle:
        messages.error(request, 'Aucune annee scolaire active.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                nouvelle_annee_libelle = f"{annee_actuelle.date_debut.year + 1}-{annee_actuelle.date_debut.year + 2}"
                
                nouvelle_annee = AnneeScolaire.objects.create(
                    libelle=nouvelle_annee_libelle,
                    date_debut=annee_actuelle.date_fin,
                    date_fin=date(annee_actuelle.date_fin.year + 1, 7, 31),
                    est_active=True,
                    type_cycle_actif=annee_actuelle.type_cycle_actif
                )
                
                CycleConfig.objects.filter(annee_scolaire=annee_actuelle).update(
                    annee_scolaire=nouvelle_annee
                )
                
                classes = Classe.objects.filter(annee_scolaire=annee_actuelle)
                nouvelle_classe_map = {}
                
                for classe in classes:
                    niveau = classe.niveau
                    niveau_suivant = get_niveau_suivant(niveau)
                    
                    nouvelle_classe = Classe.objects.create(
                        nom=classe.nom,
                        niveau=niveau_suivant if niveau_suivant else niveau,
                        filiere=classe.filiere,
                        annee_scolaire=nouvelle_annee,
                        capacite=classe.capacite,
                        professeur_principal=classe.professeur_principal
                    )
                    
                    nouvelle_classe_map[classe.id] = nouvelle_classe
                
                inscriptions = Inscription.objects.filter(
                    annee_scolaire=annee_actuelle,
                    eleve__statut='actif'
                )
                
                for inscription in inscriptions:
                    ancienne_classe = inscription.classe
                    nouvelle_classe = nouvelle_classe_map.get(ancienne_classe.id)
                    
                    if inscription.decision == 'Promu' and nouvelle_classe:
                        Inscription.objects.create(
                            eleve=inscription.eleve,
                            classe=nouvelle_classe,
                            annee_scolaire=nouvelle_annee
                        )
                        
                        FraisScolaire.objects.filter(
                            eleve=inscription.eleve,
                            annee_scolaire=annee_actuelle,
                            statut='impaye'
                        ).update(
                            annee_scolaire=nouvelle_annee,
                            statut='impaye'
                        )
                        
                    elif inscription.decision == 'Redouble' and nouvelle_classe:
                        Inscription.objects.create(
                            eleve=inscription.eleve,
                            classe=ancienne_classe,
                            annee_scolaire=nouvelle_annee
                        )
                
                annee_actuelle.est_active = False
                annee_actuelle.save()
                
                messages.success(request, f'Annee scolaire {nouvelle_annee_libelle} creee avec succes!')
                return redirect('rapports:rapport_academique')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
            return redirect('rapports:rapport_academique')
    
    return render(request, 'rapports/transition_annee.html', {
        'annee': annee_actuelle,
    })


def get_niveau_suivant(niveau):
    transitions = {
        'CI': 'CP', 'CP': 'CE1', 'CE1': 'CE2', 'CE2': 'CM1', 'CM1': 'CM2', 'CM2': '6e',
        '6e': '5e', '5e': '4e', '4e': '3e', '3e': '2nde', '2nde': '1re', '1re': 'Tle', 'Tle': None
    }
    return transitions.get(niveau)


@login_required
def bulletins_par_classe(request, classe_pk, cycle_pk=None):
    if not request.user.has_module_permission('rapports', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    classe = get_object_or_404(Classe, pk=classe_pk)
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    inscriptions = Inscription.objects.filter(classe=classe, annee_scolaire=annee) if annee else []
    return render(request, 'rapports/bulletins.html', {
        'classe': classe,
        'inscriptions': inscriptions,
        'annee': annee
    })


@login_required
def generer_bulletin(request, inscription_pk):
    if not request.user.has_module_permission('rapports', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    inscription = get_object_or_404(Inscription, pk=inscription_pk)
    messages.success(request, 'Bulletin genere.')
    return redirect('rapports:bulletin_list')


@login_required
def exporter_bulletin_pdf(request, bulletin_pk):
    if not request.user.has_module_permission('rapports', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    return HttpResponse("PDF non implemente")
