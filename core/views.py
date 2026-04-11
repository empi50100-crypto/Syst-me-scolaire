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
        
        # Note: MembrePersonnel uses 'salaire_base' instead of 'salaire_mensuel' in latest architecture
        masse_salariale_mensuelle = MembrePersonnel.objects.filter(est_actif=True).aggregate(
            total=Sum('salaire_base')
        )['total'] or 0
        
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
