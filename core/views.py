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
    
    if request.user.is_superadmin():
        context = _get_superadmin_context(annee, today)
    elif request.user.is_direction():
        context = _get_direction_context(annee, today)
    elif request.user.is_comptable():
        context = _get_comptable_context(annee, today)
    elif request.user.is_secretaire():
        context = _get_secretaire_context(annee, today)
    elif request.user.is_surveillance():
        context = _get_surveillance_context(annee, today)
    elif request.user.is_professeur():
        context = _get_professeur_context(request, annee, today)
    
    return render(request, 'core/dashboard.html', context)


def _get_superadmin_context(annee, today):
    from eleves.models import Eleve
    from academics.models import Classe
    from finances.models import Paiement, FraisScolaire, EcoleCompte, Salaire, AnneeScolaire, Personnel
    from presences.models import Presence
    from accounts.models import User
    from django.db.models import Q
    
    if not annee:
        annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    context = {
        'role': 'superadmin',
        'annee_courante': annee,
    }
    
    context['total_eleves'] = Eleve.objects.filter(statut='actif').count()
    context['total_classes'] = Classe.objects.count()
    context['total_utilisateurs'] = User.objects.filter(is_active=True).count()
    context['annee_courante'] = annee
    
    if annee:
        total_frais = _calculer_total_frais_avec_eleves(annee)
        
        total_paiements = Paiement.objects.filter(
            date_paiement__gte=annee.date_debut,
            date_paiement__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        autres_encaissements = EcoleCompte.objects.filter(
            type_operation='encaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_decaissement = EcoleCompte.objects.filter(
            type_operation='decaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_salaires = Salaire.objects.filter(
            est_paye=True,
            annee=annee.date_fin.year
        ).aggregate(Sum('salaire_net'))['salaire_net__sum'] or 0
        
        masse_salariale_mensuelle = Personnel.objects.filter(est_actif=True).aggregate(
            total=Sum('salaire_mensuel')
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
    from academics.models import Classe
    from eleves.models import Inscription
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


def _get_direction_context(annee, today):
    from eleves.models import Eleve, Inscription
    from academics.models import Classe
    from finances.models import Paiement, FraisScolaire, EcoleCompte, Salaire, AnneeScolaire, Personnel
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
        eleves_par_classe = Inscription.objects.filter(
            annee_scolaire=annee
        ).values('classe__nom').annotate(count=Count('eleve'))
        context['eleves_par_classe'] = list(eleves_par_classe)
        
        total_frais = _calculer_total_frais_avec_eleves(annee)
        
        total_paiements = Paiement.objects.filter(
            date_paiement__gte=annee.date_debut,
            date_paiement__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        autres_encaissements = EcoleCompte.objects.filter(
            type_operation='encaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_decaissement = EcoleCompte.objects.filter(
            type_operation='decaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_salaires = Salaire.objects.filter(
            est_paye=True,
            annee=annee.date_fin.year
        ).aggregate(Sum('salaire_net'))['salaire_net__sum'] or 0
        
        masse_salariale_mensuelle = Personnel.objects.filter(est_actif=True).aggregate(
            total=Sum('salaire_mensuel')
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
    
    eleves_inscrits_mois = Inscription.objects.filter(
        date_inscription__month=today.month,
        annee_scolaire=annee
    ).count()
    context['nouvelles_inscriptions'] = eleves_inscrits_mois
    
    return context


def _get_comptable_context(annee, today):
    from finances.models import Paiement, FraisScolaire, EcoleCompte, Salaire, AnneeScolaire, Personnel
    from eleves.models import Eleve, Inscription
    from academics.models import Classe
    from accounts.models import User
    from django.db.models import Sum, Q
    
    context = {
        'role': 'comptable',
        'annee_courante': annee,
    }
    
    context['total_eleves'] = Eleve.objects.filter(statut='actif').count()
    context['total_classes'] = Classe.objects.count()
    context['total_utilisateurs'] = User.objects.filter(is_active=True).count()
    context['annee_courante'] = annee
    
    if annee:
        total_frais = _calculer_total_frais_avec_eleves(annee)
        
        total_paiements = Paiement.objects.filter(
            date_paiement__gte=annee.date_debut,
            date_paiement__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        autres_encaissements = EcoleCompte.objects.filter(
            type_operation='encaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_decaissement = EcoleCompte.objects.filter(
            type_operation='decaissement',
            date_operation__gte=annee.date_debut,
            date_operation__lte=annee.date_fin
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        total_salaires = Salaire.objects.filter(
            est_paye=True,
            annee=annee.date_fin.year
        ).aggregate(Sum('salaire_net'))['salaire_net__sum'] or 0
        
        masse_salariale_mensuelle = Personnel.objects.filter(est_actif=True).aggregate(
            total=Sum('salaire_mensuel')
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
            'taux_recouvrement': round((float(total_paiements) / float(total_frais) * 100), 1) if total_frais > 0 else 0,
            'total_salaires': total_salaires,
            'masse_salariale_mensuelle': masse_salariale_mensuelle,
            'reste_a_payer': reste_a_payer,
            'nb_paiements': nb_paiements,
        })
        
        encaissements_mois = Paiement.objects.filter(
            date_paiement__year=today.year,
            date_paiement__month=today.month
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        context['encaissements_mois'] = encaissements_mois
        
        months_labels = []
        months_encaissements = []
        months_decaissements = []
        for i in range(5, -1, -1):
            d = today.replace(day=1) - timedelta(days=i*30)
            month = d.month
            year = d.year
            
            month_paiements = Paiement.objects.filter(
                date_paiement__month=month,
                date_paiement__year=year
            ).aggregate(Sum('montant'))['montant__sum'] or 0
            
            month_autres_enc = EcoleCompte.objects.filter(
                type_operation='encaissement',
                date_operation__month=month,
                date_operation__year=year
            ).aggregate(Sum('montant'))['montant__sum'] or 0
            
            month_dec = EcoleCompte.objects.filter(
                type_operation='decaissement',
                date_operation__month=month,
                date_operation__year=year
            ).aggregate(Sum('montant'))['montant__sum'] or 0
            
            month_sal = Salaire.objects.filter(
                est_paye=True,
                annee=year
            ).aggregate(Sum('salaire_net'))['salaire_net__sum'] or 0
            
            months_labels.append(calendar.month_abbr[month])
            months_encaissements.append(int(float(month_paiements) + float(month_autres_enc)))
            months_decaissements.append(int(float(month_dec) + (float(month_sal) / 12)))
        
        context['months_labels'] = months_labels
        context['months_encaissements'] = months_encaissements
        context['months_decaissements'] = months_decaissements
        
        daily_labels = []
        daily_encaissements = []
        daily_decaissements = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            daily_labels.append(d.strftime('%d/%m'))
            
            day_paiements = Paiement.objects.filter(date_paiement=d).aggregate(Sum('montant'))['montant__sum'] or 0
            day_autres_enc = EcoleCompte.objects.filter(
                type_operation='encaissement',
                date_operation=d
            ).aggregate(Sum('montant'))['montant__sum'] or 0
            
            day_dec = EcoleCompte.objects.filter(
                type_operation='decaissement',
                date_operation=d
            ).aggregate(Sum('montant'))['montant__sum'] or 0
            
            daily_encaissements.append(int(float(day_paiements) + float(day_autres_enc)))
            daily_decaissements.append(int(day_dec))
        
        context['daily_labels'] = daily_labels
        context['daily_encaissements'] = daily_encaissements
        context['daily_decaissements'] = daily_decaissements
    
    context['paiements_aujourdhui'] = Paiement.objects.filter(date_paiement=today).count()
    context['paiements_en_attente'] = Paiement.objects.filter(statut='en_attente').count() if hasattr(Paiement, 'statut') else 0
    
    return context


def _get_secretaire_context(annee, today):
    from eleves.models import Eleve, Inscription
    from academics.models import Classe
    from presences.models import Presence
    from finances.models import AnneeScolaire
    
    if not annee:
        annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    context = {
        'role': 'secretaire',
        'annee_courante': annee,
    }
    
    context['total_eleves'] = Eleve.objects.filter(statut='actif').count()
    context['total_classes'] = Classe.objects.count()
    
    if annee:
        eleves_inscrits = Inscription.objects.filter(annee_scolaire=annee).count()
        context['eleves_inscrits'] = eleves_inscrits
        
        eleves_nouveaux = Eleve.objects.filter(
            date_inscription__year=today.year,
            date_inscription__month=today.month
        ).count()
        context['eleves_nouveaux'] = eleves_nouveaux
        
        recent_inscriptions = Inscription.objects.filter(
            annee_scolaire=annee
        ).select_related('eleve', 'classe').order_by('-date_inscription')[:10]
        context['recent_inscriptions'] = list(recent_inscriptions)
    
    absents_aujourdhui = Presence.objects.filter(date=today, statut='absent').count()
    retards_aujourdhui = Presence.objects.filter(date=today, statut='retard').count()
    context['absents_aujourdhui'] = absents_aujourdhui
    context['retards_aujourdhui'] = retards_aujourdhui
    
    return context


def _get_surveillance_context(annee, today):
    from eleves.models import Eleve
    from academics.models import Classe
    from presences.models import Presence, SeanceCours
    from finances.models import AnneeScolaire
    
    if not annee:
        annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    context = {
        'role': 'surveillance',
        'annee_courante': annee,
    }
    
    context['total_eleves'] = Eleve.objects.filter(statut='actif').count()
    context['total_classes'] = Classe.objects.count()
    
    context['absents_aujourdhui'] = Presence.objects.filter(date=today, statut='absent').count()
    context['retards_aujourdhui'] = Presence.objects.filter(date=today, statut='retard').count()
    context['presents_aujourdhui'] = Presence.objects.filter(date=today, statut='present').count()
    
    presences_today = Presence.objects.filter(date=today)
    total_today = presences_today.count()
    context['taux_presence_jour'] = round((context['presents_aujourdhui'] / total_today * 100), 1) if total_today > 0 else 100
    
    cours_aujourdhui = SeanceCours.objects.filter(date=today)
    cours_en_cours = cours_aujourdhui.filter(statut=SeanceCours.Statut.EN_COURS).count()
    cours_termines = cours_aujourdhui.filter(statut=SeanceCours.Statut.TERMINEE).count()
    context['cours_en_cours'] = cours_en_cours
    context['cours_termines'] = cours_termines
    
    if annee:
        presences_semaine = Presence.objects.filter(
            date__gte=today - timedelta(days=7),
            annee_scolaire=annee
        )
        stats_semaine = {
            'present': presences_semaine.filter(statut='present').count(),
            'absent': presences_semaine.filter(statut='absent').count(),
            'retard': presences_semaine.filter(statut='retard').count(),
        }
        context['stats_semaine'] = stats_semaine
    
    return context


def _get_professeur_context(request, annee, today):
    from academics.models import Enseignement, Professeur
    from eleves.models import Inscription
    from finances.models import AnneeScolaire
    from presences.models import Presence
    
    if not annee:
        annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    context = {
        'role': 'professeur',
        'annee_courante': annee,
    }
    
    if hasattr(request.user, 'professeur') and request.user.professeur:
        prof = request.user.professeur
    else:
        prof, created = Professeur.objects.get_or_create(
            user=request.user,
            defaults={
                'nom': request.user.last_name or request.user.username,
                'prenom': request.user.first_name or request.user.username,
                'email': request.user.email,
                'date_embauche': today,
            }
        )
    
    if not annee:
        return context
    
    enseignements = Enseignement.objects.filter(
        professeur=prof,
        classe__annee_scolaire=annee
    ).select_related('classe', 'matiere')
    
    mes_classes = enseignements.values('classe').distinct().count()
    context['mes_classes'] = mes_classes
    
    total_eleves = 0
    matieres_set = set()
    for ens in enseignements:
        if ens.classe:
            eleves_count = Inscription.objects.filter(classe=ens.classe, annee_scolaire=annee).count()
            total_eleves += eleves_count
        if ens.matiere:
            matieres_set.add(ens.matiere.nom)
    
    context['total_eleves'] = total_eleves
    context['total_matieres'] = len(matieres_set)
    
    total_heures = 0
    for ens in enseignements:
        if ens.horaires:
            from datetime import datetime
            for h in ens.horaires:
                debut_str = h.get('heure_debut')
                fin_str = h.get('heure_fin')
                if debut_str and fin_str:
                    try:
                        debut = datetime.strptime(debut_str, '%H:%M')
                        fin = datetime.strptime(fin_str, '%H:%M')
                        minutes = int((fin - debut).total_seconds() / 60)
                        total_heures += minutes
                    except:
                        pass
    
    context['total_heures'] = round(total_heures / 60, 1)
    
    schedule = {jour: [] for jour in ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']}
    for ens in enseignements:
        if ens.horaires:
            for h in ens.horaires:
                jour = h.get('jour', '').lower()
                if jour in schedule:
                    schedule[jour].append({
                        'heure_debut': h.get('heure_debut'),
                        'heure_fin': h.get('heure_fin'),
                        'matiere': ens.matiere,
                        'classe': ens.classe
                    })
    context['schedule'] = schedule
    
    mes_presences = Presence.objects.filter(
        professeur=prof,
        date=today
    ).count()
    context['presences_aujourdhui'] = mes_presences
    
    return context