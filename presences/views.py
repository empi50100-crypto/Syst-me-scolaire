from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date, datetime
from .models import Presence, Appel, SeanceCours
from scolarite.models import EleveInscription
from core.models import AnneeScolaire


@login_required
def presence_list(request):
    from enseignement.models import Classe, Attribution, ProfilProfesseur
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    date_filter = request.GET.get('date', '')
    classe_filter = request.GET.get('classe', '')
    statut_filter = request.GET.get('statut', '')
    
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    if request.user.est_professeur():
        if profil_prof:
            classes = Classe.objects.filter(
                attributions__professeur=profil_prof,
                attributions__annee_scolaire=annee
            ).distinct()
            presences = Presence.objects.select_related('eleve', 'classe').filter(
                annee_scolaire=annee,
                classe__in=classes
            )
        else:
            classes = Classe.objects.none()
            presences = Presence.objects.none()
    else:
        classes = Classe.objects.filter(annee_scolaire=annee) if annee else Classe.objects.none()
        presences = Presence.objects.select_related('eleve', 'classe').filter(
            annee_scolaire=annee
        )
    
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            presences = presences.filter(date=date_obj)
        except:
            pass
    
    if classe_filter:
        presences = presences.filter(classe_id=classe_filter)
    
    if statut_filter:
        presences = presences.filter(statut=statut_filter)
    
    presences = presences.order_by('-date', '-heure_appel')
    
    presences_by_date = {}
    for p in presences:
        date_key = p.date.isoformat()
        if date_key not in presences_by_date:
            presences_by_date[date_key] = {
                'date': p.date,
                'presences': [],
                'stats': {'present': 0, 'absent': 0, 'retard': 0, 'total': 0}
            }
        presences_by_date[date_key]['presences'].append(p)
        if p.statut in presences_by_date[date_key]['stats']:
            presences_by_date[date_key]['stats'][p.statut] += 1
        presences_by_date[date_key]['stats']['total'] += 1
    
    presences_by_date = dict(sorted(presences_by_date.items(), key=lambda x: x[0], reverse=True))
    
    return render(request, 'presences/presence_list.html', {
        'presences_by_date': presences_by_date,
        'annee': annee,
        'classes': classes,
        'date_filter': date_filter,
        'classe_filter': classe_filter,
        'statut_filter': statut_filter,
    })


@login_required
def faire_appel(request, classe_pk):
    from enseignement.models import Classe
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, 'Aucune année scolaire active.')
        return redirect('dashboard')
    
    classe = get_object_or_404(Classe, pk=classe_pk)
    today = date.today()
    
    inscriptions = EleveInscription.objects.filter(
        classe=classe, annee_scolaire=annee
    ).select_related('eleve')
    
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    if request.method == 'POST':
        for ins in inscriptions:
            eleve_id = ins.eleve_id
            statut = request.POST.get(f'statut_{eleve_id}', 'present')
            
            Presence.objects.update_or_create(
                eleve_id=eleve_id,
                classe=classe,
                date=today,
                defaults={
                    'statut': statut,
                    'annee_scolaire': annee,
                    'professeur': profil_prof,
                    'observations': request.POST.get(f'observation_{eleve_id}', ''),
                }
            )
        
        messages.success(request, 'Appel enregistré avec succès.')
        return redirect('presences:presence_list')
    
    presences_existantes = {
        p.eleve_id: p.statut 
        for p in Presence.objects.filter(classe=classe, date=today)
    }
    
    inscriptions_with_presence = []
    for ins in inscriptions:
        ins.statut_present = presences_existantes.get(ins.eleve_id, 'present')
        inscriptions_with_presence.append(ins)
    
    return render(request, 'presences/faire_appel.html', {
        'classe': classe,
        'inscriptions': inscriptions_with_presence,
        'today': today,
    })


@login_required
def rapport_retards(request):
    if not request.user.has_module_permission('rapport_retards', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, 'Aucune année scolaire active.')
        return redirect('dashboard')
    
    retards = Presence.objects.filter(
        statut='retard',
        annee_scolaire=annee
    ).select_related('eleve', 'classe').order_by('-date')
    
    return render(request, 'presences/rapport_retards.html', {
        'retards': retards,
        'annee': annee,
    })


@login_required
def statistiques_presence(request):
    if not request.user.has_module_permission('statistiques_presence', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    from enseignement.models import Classe
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, 'Aucune année scolaire active.')
        return redirect('dashboard')
    
    classe_filter = request.GET.get('classe', '')
    classes = Classe.objects.filter(annee_scolaire=annee)
    
    stats_par_classe = []
    for classe in classes:
        total = Presence.objects.filter(classe=classe, annee_scolaire=annee).count()
        presents = Presence.objects.filter(classe=classe, annee_scolaire=annee, statut='present').count()
        
        taux_presence = round((presents / total * 100), 1) if total > 0 else 100
        
        stats_par_classe.append({
            'classe': classe,
            'total': total,
            'presents': presents,
            'taux_presence': taux_presence,
        })
    
    return render(request, 'presences/statistiques.html', {
        'stats_par_classe': stats_par_classe,
        'annee': annee,
        'classes': classes,
        'classe_filter': classe_filter,
    })


@login_required
def mes_seances(request):
    from enseignement.models import Attribution
    
    today = date.today()
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    seances_en_cours = SeanceCours.objects.filter(
        professeur=profil_prof,
        statut=SeanceCours.Statut.EN_COURS,
        date=today
    ).select_related('classe', 'matiere')
    
    seances_terminees = SeanceCours.objects.filter(
        professeur=profil_prof,
        date=today
    ).exclude(statut=SeanceCours.Statut.EN_COURS).select_related('classe', 'matiere')
    
    attributions = []
    if profil_prof and annee:
        attributions = Attribution.objects.filter(
            professeur=profil_prof,
            annee_scolaire=annee
        ).select_related('classe', 'matiere')
    
    return render(request, 'presences/mes_seances.html', {
        'seances_en_cours': seances_en_cours,
        'seances_terminees': seances_terminees,
        'attributions': attributions,
        'today': today,
    })


@login_required
def demarrer_seance(request, attribution_id):
    from enseignement.models import Attribution
    from authentification.models import Notification, Utilisateur
    
    today = date.today()
    maintenant = datetime.now().time()
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    ens = get_object_or_404(Attribution, pk=attribution_id)
    
    if request.method == 'POST':
        seance = SeanceCours.objects.create(
            professeur=profil_prof,
            classe=ens.classe,
            matiere=ens.matiere,
            date=today,
            heure_debut=maintenant,
            annee_scolaire=annee,
            statut=SeanceCours.Statut.EN_COURS,
            creee_par=request.user
        )
        
        users_notif = Utilisateur.objects.filter(
            role__in=[Utilisateur.Role.DIRECTION, Utilisateur.Role.SUPERADMIN, Utilisateur.Role.SURVEILLANCE]
        )
        for user in users_notif:
            # Note: notification logic might need adaptation based on actual model
            pass
        
        messages.success(request, f'Cours démarré dans la classe {ens.classe.nom}.')
        return redirect('presences:mes_seances')
    
    return render(request, 'presences/demarrer_seance.html', {'ens': ens})


@login_required
def terminer_seance(request, seance_id):
    profil_prof = getattr(request.user, 'profil_professeur', None)
    seance = get_object_or_404(SeanceCours, pk=seance_id, professeur=profil_prof)
    
    if request.method == 'POST':
        seance.heure_fin = datetime.now().time()
        seance.statut = SeanceCours.Statut.TERMINEE
        seance.notes = request.POST.get('notes', '')
        seance.save()
        messages.success(request, 'Cours terminé.')
        return redirect('presences:mes_seances')
    
    return render(request, 'presences/terminer_seance.html', {'seance': seance})


@login_required
def liste_seances(request):
    today = request.GET.get('date', date.today().isoformat())
    try:
        today_date = datetime.strptime(today, '%Y-%m-%d').date()
    except:
        today_date = date.today()
    
    seances = SeanceCours.objects.filter(date=today_date).select_related('professeur__user', 'classe', 'matiere')
    
    return render(request, 'presences/liste_seances.html', {
        'seances': seances,
        'today': today_date,
    })


@login_required
def attestation_assiduite_form(request):
    """Formulaire pour sélectionner un élève et générer une attestation d'assiduité"""
    from scolarite.models import Eleve
    from django.db.models import Q
    
    eleves = Eleve.objects.filter(est_actif=True).order_by('nom', 'prenom')
    
    # Handle search
    search = request.GET.get('search', '')
    if search:
        eleves = eleves.filter(
            Q(nom__icontains=search) | 
            Q(prenom__icontains=search) | 
            Q(matricule__icontains=search)
        )
    
    if request.method == 'POST':
        eleve_pk = request.POST.get('eleve')
        if eleve_pk:
            return redirect('presences:attestation_assiduite_pdf', eleve_pk=eleve_pk)
    
    return render(request, 'presences/attestation_form.html', {
        'eleves': eleves,
        'search': search,
    })


@login_required
def attestation_assiduite_pdf(request, eleve_pk):
    # PDF generation logic...
    return HttpResponse("PDF non implémenté")
