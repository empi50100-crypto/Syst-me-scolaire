from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import date, timedelta
import calendar


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/landing.html')


def landing_page(request):
    return render(request, 'core/landing.html')


@login_required
def dashboard(request):
    context = {}
    annee = getattr(request, 'annee_active', None)
    today = date.today()
    role = request.user.role
    
    if request.user.est_superadmin():
        context = _get_superadmin_context(annee, today)
    elif request.user.est_direction():
        context = _get_direction_context(annee, today)
    elif request.user.est_comptable():
        context = _get_comptable_context(annee, today)
    elif request.user.est_secretaire():
        context = _get_secretaire_context(annee, today)
    elif request.user.est_surveillance():
        context = _get_surveillance_context(annee, today)
    elif request.user.est_professeur():
        context = _get_professeur_context(request, annee, today)
    
    context['role'] = role
    return render(request, 'core/dashboard.html', context)


def _get_superadmin_context(annee, today):
    from scolarite.models import Eleve, EleveInscription
    from enseignement.models import Classe
    from finances.models import Paiement, FraisScolaire, OperationCaisse
    from ressources_humaines.models import Salaire, MembrePersonnel
    from core.models import AnneeScolaire
    from presences.models import Presence
    from authentification.models import Utilisateur
    from django.db.models import Q
    
    if not annee:
        annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    context = {
        'role': 'superadmin',
        'annee_courante': annee,
    }
    
    context['total_eleves'] = Eleve.objects.filter(statut='actif').count()
    context['total_classes'] = Classe.objects.count()
    context['total_utilisateurs'] = Utilisateur.objects.filter(is_active=True).count()
    context['annee_courante'] = annee
    
    if annee:
        total_frais = _calculer_total_frais_avec_eleves(annee)
        
        total_paiements = Paiement.objects.filter(
            date_paiement__gte=annee.date_debut,
            date_paiement__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        autres_encaissements = OperationCaisse.objects.filter(
            type_operation='encaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_decaissement = OperationCaisse.objects.filter(
            type_operation='decaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_salaires = Salaire.objects.filter(
            est_paye=True,
            annee=annee.date_fin.year
        ).aggregate(Sum('salaire_net'))['salaire_net__sum'] or 0
        
        masse_salariale_mensuelle = Salaire.objects.filter(
            employe__est_actif=True,
            est_paye=True
        ).aggregate(total=Sum('salaire_brut'))['total'] or 0
        
        total_encaissé = float(total_paiements) + float(autres_encaissements)
        total_charges = float(total_decaissement) + float(total_salaires)
        reste_a_payer = float(total_frais) - float(total_paiements)
        nb_paiements = Paiement.objects.filter(
            date_paiement__gte=annee.date_debut,
            date_paiement__lte=annee.date_fin
        ).count()
        
        context.update({
            'total_frais': total_frais,
            'total_encaissé': total_encaissé,
            'total_decaissement': total_charges,
            'montant_restant': total_encaissé - total_charges,
            'reste_a_payer': reste_a_payer,
            'taux_recouvrement': round((float(total_paiements) / float(total_frais) * 100), 1) if total_frais > 0 else 0,
            'paiements_aujourdhui': Paiement.objects.filter(date_paiement=today).count(),
            'paiements_mois': Paiement.objects.filter(date_paiement__month=today.month).count(),
            'nb_paiements': nb_paiements,
            'total_salaires': total_salaires,
            'masse_salariale_mensuelle': masse_salariale_mensuelle,
            'encaissements_mois': Paiement.objects.filter(
                date_paiement__month=today.month,
                date_paiement__year=today.year
            ).aggregate(Sum('montant'))['montant__sum'] or 0,
        })
    
    contexte_presence = {'annee_scolaire': annee} if annee else {}
    total_present = Presence.objects.filter(statut='present', **contexte_presence).count()
    total_absent = Presence.objects.filter(statut='absent', **contexte_presence).count()
    total_retard = Presence.objects.filter(statut='retard', **contexte_presence).count()
    total_presence = total_present + total_absent + total_retard
    context['taux_presence_global'] = round((total_present / total_presence * 100), 1) if total_presence > 0 else 100
    
    context['eleves_nouveaux'] = Eleve.objects.filter(date_inscription__month=today.month).count()
    context['eleves_inscrits'] = Eleve.objects.filter(statut='actif').count()
    
    return context


def _calculer_total_frais_avec_eleves(annee):
    from finances.models import FraisScolaire
    from enseignement.models import Classe
    from scolarite.models import EleveInscription
    from django.db.models import Q
    
    total_frais = 0
    frais_list = FraisScolaire.objects.filter(
        Q(annee_scolaire=annee) | Q(annee_scolaire__isnull=True)
    )
    
    for frais in frais_list:
        # get_classes_concernees needs to be implemented in FraisScolaire or handled here
        # For now, we assume it's a list or handled by the model
        if hasattr(frais, 'get_classes_concernees'):
            classes_concernees = frais.get_classes_concernees()
        elif frais.classe:
            classes_concernees = [frais.classe]
        elif frais.niveau:
            classes_concernees = Classe.objects.filter(niveau=frais.niveau, annee_scolaire=annee)
        else:
            classes_concernees = Classe.objects.filter(annee_scolaire=annee)
            
        nb_eleves = EleveInscription.objects.filter(
            annee_scolaire=annee,
            classe__in=classes_concernees
        ).count()
        total_frais += float(frais.montant) * nb_eleves
    
    return total_frais


def _get_direction_context(annee, today):
    from scolarite.models import Eleve, EleveInscription
    from enseignement.models import Classe
    from finances.models import Paiement, FraisScolaire, OperationCaisse
    from ressources_humaines.models import Salaire, MembrePersonnel
    from core.models import AnneeScolaire
    from presences.models import Presence
    from django.db.models import Q
    
    if not annee:
        annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    context = {
        'role': 'direction',
        'annee_courante': annee,
    }
    
    context['total_eleves'] = Eleve.objects.filter(statut='actif').count()
    context['total_classes'] = Classe.objects.count()
    context['annee_courante'] = annee
    
    if annee:
        eleves_par_classe = EleveInscription.objects.filter(
            annee_scolaire=annee
        ).values('classe__nom').annotate(count=Count('eleve'))
        context['eleves_par_classe'] = list(eleves_par_classe)
        
        total_frais = _calculer_total_frais_avec_eleves(annee)
        
        total_paiements = Paiement.objects.filter(
            date_paiement__gte=annee.date_debut,
            date_paiement__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        autres_encaissements = OperationCaisse.objects.filter(
            type_operation='encaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_decaissement = OperationCaisse.objects.filter(
            type_operation='decaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_salaires = Salaire.objects.filter(
            est_paye=True,
            annee=annee.date_fin.year
        ).aggregate(Sum('salaire_net'))['salaire_net__sum'] or 0
        
        masse_salariale_mensuelle = MembrePersonnel.objects.filter(est_actif=True).aggregate(
            total=Sum('salaire_base')
        )['total'] or 0
        
        total_encaissé = float(total_paiements) + float(autres_encaissements)
        total_charges = float(total_decaissement) + float(total_salaires)
        
        context['total_frais'] = total_frais
        context['total_encaissé'] = total_encaissé
        context['total_decaissement'] = total_charges
        context['montant_restant'] = total_encaissé - total_charges
        context['taux_recouvrement'] = round((float(total_paiements) / float(total_frais) * 100), 1) if total_frais > 0 else 0
        context['masse_salariale_mensuelle'] = masse_salariale_mensuelle
        context['reste_a_payer'] = float(total_frais) - float(total_paiements)
        context['nb_paiements'] = Paiement.objects.filter(
            date_paiement__gte=annee.date_debut,
            date_paiement__lte=annee.date_fin
        ).count()
    
    contexte_presence = {'annee_scolaire': annee} if annee else {}
    total_present = Presence.objects.filter(statut='present', **contexte_presence).count()
    total_absent = Presence.objects.filter(statut='absent', **contexte_presence).count()
    total_retard = Presence.objects.filter(statut='retard', **contexte_presence).count()
    total_presence = total_present + total_absent + total_retard
    context['taux_presence_global'] = round((total_present / total_presence * 100), 1) if total_presence > 0 else 100
    context['absents_aujourdhui'] = Presence.objects.filter(date=today, statut='absent').count()
    
    eleves_inscrits_mois = EleveInscription.objects.filter(
        date_inscription__month=today.month,
        annee_scolaire=annee
    ).count()
    context['nouvelles_inscriptions'] = eleves_inscrits_mois
    
    return context


def _get_comptable_context(annee, today):
    from finances.models import Paiement, FraisScolaire, OperationCaisse
    from ressources_humaines.models import Salaire, MembrePersonnel
    from scolarite.models import Eleve, EleveInscription
    from enseignement.models import Classe
    from core.models import AnneeScolaire
    from authentification.models import Utilisateur
    from django.db.models import Sum, Q
    
    context = {
        'role': 'comptable',
        'annee_courante': annee,
    }
    
    context['total_eleves'] = Eleve.objects.filter(statut='actif').count()
    context['total_classes'] = Classe.objects.count()
    context['total_utilisateurs'] = Utilisateur.objects.filter(is_active=True).count()
    
    if annee:
        total_frais = _calculer_total_frais_avec_eleves(annee)
        total_paiements = Paiement.objects.filter(
            date_paiement__gte=annee.date_debut,
            date_paiement__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        context['total_frais'] = total_frais
        context['total_paiements'] = total_paiements
        context['taux_recouvrement'] = round((float(total_paiements) / float(total_frais) * 100), 1) if total_frais > 0 else 0
        context['paiements_aujourdhui'] = Paiement.objects.filter(date_paiement=today).count()
        
        # Recent transactions
        context['derniers_paiements'] = Paiement.objects.filter(
            date_paiement__lte=today
        ).order_by('-date_paiement')[:10]
        
    return context


def _get_secretaire_context(annee, today):
    from scolarite.models import Eleve, EleveInscription
    from enseignement.models import Classe
    from core.models import AnneeScolaire
    
    context = {
        'role': 'secretaire',
        'annee_courante': annee,
    }
    
    context['total_eleves'] = Eleve.objects.filter(statut='actif').count()
    context['total_classes'] = Classe.objects.count()
    
    if annee:
        context['inscriptions_recentes'] = EleveInscription.objects.filter(
            annee_scolaire=annee
        ).order_by('-date_inscription')[:10]
        
        context['nouvelles_inscriptions'] = EleveInscription.objects.filter(
            date_inscription__month=today.month,
            annee_scolaire=annee
        ).count()
        
    return context


def _get_surveillance_context(annee, today):
    from presences.models import Presence, Appel
    from scolarite.models import Eleve
    from core.models import AnneeScolaire
    
    context = {
        'role': 'surveillance',
        'annee_courante': annee,
    }
    
    context['absents_aujourdhui'] = Presence.objects.filter(date=today, statut='absent').count()
    context['retards_aujourdhui'] = Presence.objects.filter(date=today, statut='retard').count()
    
    if annee:
        context['derniers_appels'] = Appel.objects.filter(
            date=today
        ).order_by('-heure_debut')[:10]
        
    return context


def _get_professeur_context(request, annee, today):
    from enseignement.models import Classe, Attribution, Evaluation
    from presences.models import SeanceCours
    from core.models import AnneeScolaire
    
    professeur = getattr(request.user, 'profil_professeur', None)
    
    context = {
        'role': 'professeur',
        'annee_courante': annee,
    }
    
    if professeur:
        attributions = Attribution.objects.filter(professeur=professeur, annee_scolaire=annee)
        context['mes_classes'] = Classe.objects.filter(attributions__in=attributions).distinct()
        context['mes_seances'] = SeanceCours.objects.filter(professeur=professeur, date=today)
        context['dernieres_evaluations'] = Evaluation.objects.filter(
            classe__attributions__professeur=professeur
        ).order_by('-date_eval')[:10]
        
    return context


@login_required
def cycle_list(request):
    from .models import Cycle, AnneeScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    annee = getattr(request, 'annee_active', None)
    cycles = Cycle.objects.all()
    if annee:
        cycles = cycles.filter(annee_scolaire=annee)
    
    return render(request, 'core/cycle_list.html', {'cycles': cycles, 'annee': annee})


@login_required
def cycle_create(request):
    from .models import Cycle, AnneeScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    if request.method == 'POST':
        annee_id = request.POST.get('annee_scolaire')
        type_cycle = request.POST.get('type_cycle')
        numero = request.POST.get('numero')
        debut = request.POST.get('debut')
        fin = request.POST.get('fin')
        
        annee = AnneeScolaire.objects.get(pk=annee_id) if annee_id else getattr(request, 'annee_active', None)
        
        Cycle.objects.create(
            annee_scolaire=annee,
            type_cycle=type_cycle,
            numero=int(numero),
            date_debut=debut,
            date_fin=fin
        )
        return redirect('/core/cycles/')
    
    annees = AnneeScolaire.objects.all()
    annee_active = getattr(request, 'annee_active', None)
    type_cycle_par_defaut = annee_active.type_cycle_actif if annee_active else None
    return render(request, 'core/cycle_form.html', {'annees': annees, 'annee_active': annee_active, 'type_cycle_par_defaut': type_cycle_par_defaut})


@login_required
def cycle_edit(request, pk):
    from .models import Cycle, AnneeScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    cycle = Cycle.objects.get(pk=pk)
    
    if request.method == 'POST':
        cycle.type_cycle = request.POST.get('type_cycle')
        cycle.numero = int(request.POST.get('numero'))
        cycle.date_debut = request.POST.get('debut')
        cycle.date_fin = request.POST.get('fin')
        cycle.save()
        return redirect('/core/cycles/')
    
    annees = AnneeScolaire.objects.all()
    return render(request, 'core/cycle_edit.html', {'cycle': cycle, 'annees': annees})


@login_required
def cycle_delete(request, pk):
    from .models import Cycle
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    cycle = Cycle.objects.get(pk=pk)
    cycle.delete()
    return redirect('/core/cycles/')


@login_required
def niveau_list(request):
    from .models import NiveauScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    niveaux = NiveauScolaire.objects.all().order_by('ordre')
    return render(request, 'core/niveau_list.html', {'niveaux': niveaux})


@login_required
def niveau_create(request):
    from .models import NiveauScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    if request.method == 'POST':
        from .models import NiveauScolaire
        niveau = request.POST.get('niveau')
        libelle = request.POST.get('libelle')
        ordre = request.POST.get('ordre')
        
        if NiveauScolaire.objects.filter(niveau=niveau).exists():
            return render(request, 'core/niveau_form.html', {
                'error': f'Le niveau "{niveau}" existe déjà. Choisissez un autre niveau.'
            })
        
        NiveauScolaire.objects.create(
            niveau=niveau,
            libelle=libelle,
            ordre=int(ordre) if ordre else 0
        )
        return redirect('/core/niveaux/')
    
    return render(request, 'core/niveau_form.html')


@login_required
def niveau_edit(request, pk):
    from .models import NiveauScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    niveau = NiveauScolaire.objects.get(pk=pk)
    
    if request.method == 'POST':
        niveau.libelle = request.POST.get('libelle')
        niveau.ordre = int(request.POST.get('ordre', 0))
        niveau.save()
        return redirect('/core/niveaux/')
    
    return render(request, 'core/niveau_edit.html', {'niveau': niveau})


@login_required
def niveau_delete(request, pk):
    from .models import NiveauScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    niveau = NiveauScolaire.objects.get(pk=pk)
    niveau.delete()
    return redirect('/core/niveaux/')


@login_required
def periode_list(request):
    from .models import PeriodeEvaluation, AnneeScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    annee = getattr(request, 'annee_active', None)
    periodes = PeriodeEvaluation.objects.all()
    if annee:
        periodes = periodes.filter(annee_scolaire=annee)
    
    return render(request, 'core/periode_list.html', {'periodes': periodes, 'annee': annee})


@login_required
def periode_create(request):
    from .models import PeriodeEvaluation, AnneeScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    annees = AnneeScolaire.objects.all()
    annee_active = getattr(request, 'annee_active', None)
    
    if request.method == 'POST':
        annee_id = request.POST.get('annee_scolaire')
        type_periode = request.POST.get('type_periode')
        numero = request.POST.get('numero')
        debut = request.POST.get('debut')
        fin = request.POST.get('fin')
        
        annee = AnneeScolaire.objects.get(pk=annee_id) if annee_id else annee_active
        
        # Plus de vérification de doublon - on peut avoir plusieurs périodes par semestre
        
        PeriodeEvaluation.objects.create(
            annee_scolaire=annee,
            type_periode=type_periode,
            numero=int(numero),
            debut=debut,
            fin=fin
        )
        return redirect('/core/periodes/')
    
    annees = AnneeScolaire.objects.all()
    annee_active = getattr(request, 'annee_active', None)
    
    type_periode_par_defaut = 'trimestre'
    if annee_active and annee_active.type_cycle_actif:
        if annee_active.type_cycle_actif == 'trimestriel':
            type_periode_par_defaut = 'trimestre'
        else:
            type_periode_par_defaut = 'semestre'
    
    return render(request, 'core/periode_form.html', {
        'annees': annees, 
        'annee_active': annee_active,
        'type_periode_par_defaut': type_periode_par_defaut
    })


@login_required
def periode_edit(request, pk):
    from .models import PeriodeEvaluation, AnneeScolaire
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    periode = PeriodeEvaluation.objects.get(pk=pk)
    annees = AnneeScolaire.objects.all()
    
    if request.method == 'POST':
        type_periode = request.POST.get('type_periode')
        numero = int(request.POST.get('numero'))
        
        # Check for duplicate
        existe = PeriodeEvaluation.objects.filter(
            annee_scolaire=periode.annee_scolaire,
            type_periode=type_periode,
            numero=numero
        ).exclude(pk=pk).exists()
        
        if existe:
            return render(request, 'core/periode_edit.html', {
                'periode': periode,
                'annees': annees,
                'error': f'Une période avec {type_periode} {numero} existe déjà.'
            })
        
        periode.type_periode = type_periode
        periode.numero = numero
        periode.debut = request.POST.get('debut')
        periode.fin = request.POST.get('fin')
        periode.save()
        return redirect('/core/periodes/')
    
    return render(request, 'core/periode_edit.html', {'periode': periode, 'annees': annees})


@login_required
def periode_delete(request, pk):
    from .models import PeriodeEvaluation
    if not request.user.est_superadmin() and not request.user.est_direction():
        return redirect('dashboard')
    
    periode = PeriodeEvaluation.objects.get(pk=pk)
    periode.delete()
    return redirect('/core/periodes/')
