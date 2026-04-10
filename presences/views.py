from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from datetime import date, datetime, timedelta, time
from .models import Presence, Appel, SeanceCours
from .forms import PresenceForm, AppelForm
from eleves.models import Inscription
from finances.models import AnneeScolaire


def is_direction_or_surveillance(user):
    return user.is_authenticated and (user.is_direction() or user.is_surveillance() or user.is_superadmin())


def is_professeur(user):
    return user.is_authenticated and user.is_professeur()


@login_required
def presence_list(request):
    from academics.models import Classe, Enseignement, Professeur
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    date_filter = request.GET.get('date', '')
    classe_filter = request.GET.get('classe', '')
    statut_filter = request.GET.get('statut', '')
    
    if request.user.is_professeur():
        if not hasattr(request.user, 'professeur') or not request.user.professeur:
            prof, created = Professeur.objects.get_or_create(
                user=request.user,
                defaults={
                    'nom': request.user.last_name or request.user.username,
                    'prenom': request.user.first_name or request.user.username,
                    'email': request.user.email,
                    'date_embauche': date.today(),
                }
            )
        
        if hasattr(request.user, 'professeur') and request.user.professeur:
            classes = Classe.objects.filter(
                enseignements__professeur=request.user.professeur,
                enseignements__annee_scolaire=annee
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
    from academics.models import Classe
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, 'Aucune année scolaire active.')
        return redirect('dashboard')
    
    classe = get_object_or_404(Classe, pk=classe_pk)
    today = date.today()
    
    inscriptions = Inscription.objects.filter(
        classe=classe, annee_scolaire=annee
    ).select_related('eleve')
    
    if request.method == 'POST':
        for inscription in inscriptions:
            eleve_id = inscription.eleve_id
            statut = request.POST.get(f'statut_{eleve_id}', 'present')
            
            Presence.objects.update_or_create(
                eleve_id=eleve_id,
                classe=classe,
                date=today,
                defaults={
                    'statut': statut,
                    'annee_scolaire': annee,
                    'professeur': request.user.professeur if request.user.is_professeur() else None,
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
        messages.error(request, "Vous n'avez pas l'autorisation de voir les rapports de retards.")
        return redirect('dashboard')
    
    from datetime import timedelta
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, 'Aucune année scolaire active.')
        return redirect('dashboard')
    
    retards = Presence.objects.filter(
        statut='retard',
        annee_scolaire=annee
    ).select_related('eleve', 'classe').order_by('-date')
    
    eleves_avec_retards = {}
    for r in retards:
        key = r.eleve_id
        if key not in eleves_avec_retards:
            eleves_avec_retards[key] = {'eleve': r.eleve, 'classe': r.classe, 'count': 0}
        eleves_avec_retards[key]['count'] += 1
    
    return render(request, 'presences/rapport_retards.html', {
        'retards': retards,
        'eleves_avec_retards': eleves_avec_retards,
        'annee': annee,
    })


@login_required
def statistiques_presence(request):
    if not request.user.has_module_permission('statistiques_presence', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les statistiques de présence.")
        return redirect('dashboard')
    
    from academics.models import Classe
    from django.db.models import Count
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, 'Aucune année scolaire active.')
        return redirect('dashboard')
    
    classe_filter = request.GET.get('classe', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    
    classes = Classe.objects.filter(annee_scolaire=annee)
    
    filters = {'annee_scolaire': annee}
    if classe_filter:
        filters['classe_id'] = classe_filter
    if date_debut:
        try:
            filters['date__gte'] = datetime.strptime(date_debut, '%Y-%m-%d').date()
        except:
            pass
    if date_fin:
        try:
            filters['date__lte'] = datetime.strptime(date_fin, '%Y-%m-%d').date()
        except:
            pass
    
    stats_par_classe = []
    for classe in classes:
        base_filter = {**filters, 'classe': classe}
        total = Presence.objects.filter(**base_filter).count()
        absents = Presence.objects.filter(**base_filter, statut='absent').count()
        retards = Presence.objects.filter(**base_filter, statut='retard').count()
        presents = Presence.objects.filter(**base_filter, statut='present').count()
        
        taux_presence = round((presents / total * 100), 1) if total > 0 else 100
        taux_absence = round((absents / total * 100), 1) if total > 0 else 0
        
        stats_par_classe.append({
            'classe': classe,
            'total': total,
            'absents': absents,
            'retards': retards,
            'presents': presents,
            'taux_presence': taux_presence,
            'taux_absence': taux_absence,
        })
    
    total_global = sum(s['total'] for s in stats_par_classe)
    total_absents = sum(s['absents'] for s in stats_par_classe)
    total_retards = sum(s['retards'] for s in stats_par_classe)
    total_presents = sum(s['presents'] for s in stats_par_classe)
    taux_global = round((total_presents / total_global * 100), 1) if total_global > 0 else 100
    
    return render(request, 'presences/statistiques.html', {
        'stats_par_classe': stats_par_classe,
        'annee': annee,
        'classes': classes,
        'classe_filter': classe_filter,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'total_global': total_global,
        'total_absents': total_absents,
        'total_retards': total_retards,
        'total_presents': total_presents,
        'taux_global': taux_global,
    })


def is_professeur(user):
    return user.is_authenticated and user.is_professeur()


@login_required
def mes_seances(request):
    if not request.user.has_module_permission('mes_seances', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir vos séances.")
        return redirect('dashboard')
    
    from academics.models import Enseignement, Professeur
    from django.db.models import Q
    
    today = date.today()
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    if hasattr(request.user, 'professeur'):
        prof = request.user.professeur
    else:
        prof = None
    
    seances_en_cours = SeanceCours.objects.filter(
        professeur=prof,
        statut=SeanceCours.Statut.EN_COURS,
        date=today
    ).select_related('classe', 'matiere')
    
    seances_terminees = SeanceCours.objects.filter(
        professeur=prof,
        date=today
    ).exclude(statut=SeanceCours.Statut.EN_COURS).select_related('classe', 'matiere')
    
    enseignements = []
    if prof and annee:
        enseignements = Enseignement.objects.filter(
            Q(professeur=prof) | Q(professeur__user=request.user),
            classe__annee_scolaire=annee
        ).select_related('classe', 'matiere')
    
    return render(request, 'presences/mes_seances.html', {
        'seances_en_cours': seances_en_cours,
        'seances_terminees': seances_terminees,
        'enseignements': enseignements,
        'today': today,
    })


@login_required
def demarrer_seance(request, seance_id):
    if not request.user.has_module_permission('mes_seances', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de démarrer une séance.")
        return redirect('presences:mes_seances')
    
    from academics.models import Enseignement, Professeur
    from accounts.models import Notification
    
    today = date.today()
    maintenant = datetime.now().time()
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    if hasattr(request.user, 'professeur'):
        prof = request.user.professeur
    else:
        prof = None
    
    ens = get_object_or_404(Enseignement, pk=seance_id)
    
    if request.method == 'POST':
        seance = SeanceCours.objects.create(
            professeur=prof,
            classe=ens.classe,
            matiere=ens.matiere,
            date=today,
            heure_debut=maintenant,
            annee_scolaire=annee,
            statut=SeanceCours.Statut.EN_COURS,
            creee_par=request.user
        )
        
        from accounts.models import User
        users_direction = User.objects.filter(
            Q(role__in=[User.Role.DIRECTION, User.Role.SUPERADMIN]) | Q(role=User.Role.SURVEILLANCE)
        )
        for user in users_direction:
            Notification.creer_notification(
                destinataire=user,
                type_notification=Notification.TypeNotification.DEBUT_COURS,
                titre=f'Début de cours - {prof}',
                message=f'Le professeur {prof} a démarré son cours de {ens.matiere} dans la classe {ens.classe.nom}.',
                lien=f'/presences/seances/'
            )
        
        messages.success(request, f'Cours démarré dans la classe {ens.classe.nom}.')
        return redirect('presences:mes_seances')
    
    return render(request, 'presences/demarrer_seance.html', {
        'ens': ens,
        'seance': seance if 'seance' in locals() else None,
    })


@login_required
def terminer_seance(request, seance_id):
    if not request.user.has_module_permission('mes_seances', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de terminer une séance.")
        return redirect('presences:mes_seances')
    
    from accounts.models import Notification
    from django.db.models import Q
    
    maintenant = datetime.now()
    seance = get_object_or_404(SeanceCours, pk=seance_id, professeur=request.user.professeur)
    
    if request.method == 'POST':
        seance.heure_fin = maintenant.time()
        
        debut_dt = datetime.combine(seance.date, seance.heure_debut) if seance.heure_debut else maintenant
        duree = int((maintenant - datetime.combine(seance.date, seance.heure_debut)).total_seconds() / 60) if seance.heure_debut else 0
        
        seance.duree_minutes = duree
        seance.statut = SeanceCours.Statut.TERMINEE
        seance.notes = request.POST.get('notes', '')
        seance.save()
        
        from accounts.models import User
        users_direction = User.objects.filter(
            Q(role__in=[User.Role.DIRECTION, User.Role.SUPERADMIN]) | Q(role=User.Role.SURVEILLANCE)
        )
        for user in users_direction:
            Notification.creer_notification(
                destinataire=user,
                type_notification=Notification.TypeNotification.FIN_COURS,
                titre=f'Fin de cours - {seance.professeur}',
                message=f'Le professeur {seance.professeur} a terminé son cours de {seance.matiere} dans la classe {seance.classe.nom}. Durée: {seance.duree_formatee()}',
                lien=f'/presences/seances/'
            )
        
        messages.success(request, f'Cours terminé. Durée: {seance.duree_formatee()}')
        return redirect('presences:mes_seances')
    
    return render(request, 'presences/terminer_seance.html', {
        'seance': seance,
    })


@login_required
def liste_seances(request):
    if not request.user.has_module_permission('mes_seances', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les séances.")
        return redirect('dashboard')
    
    today = request.GET.get('date', date.today())
    if isinstance(today, str):
        try:
            today = datetime.strptime(today, '%Y-%m-%d').date()
        except:
            today = date.today()
    
    seances = SeanceCours.objects.filter(date=today).select_related('professeur', 'classe', 'matiere')
    
    seances_en_cours = seances.filter(statut=SeanceCours.Statut.EN_COURS)
    seances_terminees = seances.filter(statut=SeanceCours.Statut.TERMINEE)
    
    return render(request, 'presences/liste_seances.html', {
        'seances': seances,
        'seances_en_cours': seances_en_cours,
        'seances_terminees': seances_terminees,
        'today': today,
    })


@login_required
def attestation_assiduite_pdf(request, eleve_pk):
    if not request.user.has_module_permission('presence_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de générer des attestations.")
        return redirect('dashboard')
    
    from eleves.models import Eleve
    from io import BytesIO
    from django.db.models import Count
    
    eleve = get_object_or_404(Eleve, pk=eleve_pk)
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    if not annee:
        messages.error(request, 'Aucune année scolaire active.')
        return redirect('presences:presence_list')
    
    inscription = Inscription.objects.filter(eleve=eleve, annee_scolaire=annee).first()
    classe = inscription.classe if inscription else None
    
    presences = Presence.objects.filter(eleve=eleve, annee_scolaire=annee)
    total_jours = presences.count()
    jours_presents = presences.filter(statut='present').count()
    jours_absents = presences.filter(statut='absent').count()
    jours_retards = presences.filter(statut='retard').count()
    
    taux_presence = round((jours_presents / total_jours * 100), 1) if total_jours > 0 else 100
    
    buffer = BytesIO()
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
    
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18, spaceAfter=10)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, spaceAfter=20)
    header_style = ParagraphStyle('Header', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=14, spaceAfter=30)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY, spaceAfter=12)
    right_style = ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=10)
    
    elements.append(Paragraph("ATTESTATION D'ASSIDUITÉ", title_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Année Scolaire : {annee.libelle}", subtitle_style))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph(
        "Le Directeur de l'établissement scolaires certify que l'élève :",
        body_style
    ))
    elements.append(Spacer(1, 15))
    
    student_data = [
        ['Nom et Prénom :', f"{eleve.nom} {eleve.prenom}"],
        ['Matricule :', eleve.matricule or 'N/A'],
        ['Classe :', classe.nom if classe else 'Non classé'],
        ['Date de naissance :', eleve.date_naissance.strftime('%d/%m/%Y') if eleve.date_naissance else 'N/A'],
    ]
    
    student_table = Table(student_data, colWidths=[80*mm, 90*mm])
    student_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 25))
    
    elements.append(Paragraph(
        f"A fréquenté régulièrement notre établissement durant la période du {annee.date_debut.strftime('%d/%m/%Y')} au {annee.date_fin.strftime('%d/%m/%Y')}.",
        body_style
    ))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Bilan de présence :", styles['Heading3']))
    elements.append(Spacer(1, 10))
    
    stats_data = [
        ['Jours de présence', str(jours_presents)],
        ['Jours d\'absence', str(jours_absents)],
        ['Retards', str(jours_retards)],
        ['Taux d\'assiduité', f"{taux_presence}%"],
    ]
    
    stats_table = Table(stats_data, colWidths=[70*mm, 30*mm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.95, 0.95, 0.95)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 40))
    
    elements.append(Paragraph(
        "Cette attestation est délivrée pour servir et valoir ce que de droit.",
        body_style
    ))
    elements.append(Spacer(1, 40))
    
    from datetime import datetime
    lieu_date = Paragraph(f"Fait à ..................., le {datetime.now().strftime('%d/%m/%Y')}", right_style)
    elements.append(lieu_date)
    elements.append(Spacer(1, 50))
    
    signature_table = Table([['Le Directeur', '']], colWidths=[85*mm, 85*mm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(signature_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"Attestation_Assiduite_{eleve.nom}_{eleve.prenom}_{annee.libelle.replace('/', '-')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def attestation_assiduite_form(request):
    from eleves.models import Eleve
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    eleves = Eleve.objects.filter(statut='actif').order_by('nom', 'prenom')
    
    search = request.GET.get('search', '')
    if search:
        eleves = eleves.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(matricule__icontains=search)
        )
    
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve')
        if eleve_id:
            return redirect('attestation_assiduite_pdf', eleve_pk=eleve_id)
    
    return render(request, 'presences/attestation_form.html', {
        'eleves': eleves,
        'annee': annee,
        'search': search,
    })
