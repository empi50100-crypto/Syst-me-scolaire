from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q, Count
from django.http import HttpResponse
from datetime import datetime
import csv

from scolarite.models import (
    Eleve, ParentTuteur, DossierMedical, DocumentEleve,
    CloturePeriode, ClotureNotes, SanctionRecompense,
    EleveInscription, ConfigurationConduite, ConduiteEleve,
    ClotureAnneeScolaire
)
from scolarite.forms import EleveForm, DocumentFormSet
from core.models import AnneeScolaire
from enseignement.models import Classe
from authentification.models import Utilisateur, JournalAudit


def log_audit_helper(utilisateur, action, model, obj=None, details='', request=None):
    """Helper to log actions in the audit journal"""
    from authentification.models import log_audit
    return log_audit(utilisateur, action, model, obj, details, request)


@login_required
def eleve_list(request):
    if not request.user.has_module_permission('eleve_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les élèves.")
        return redirect('dashboard')
    
    eleves_qs = Eleve.objects.all().order_by('nom', 'prenom')
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    search = request.GET.get('search', '')
    niveau_id = request.GET.get('niveau', '')
    classe_id = request.GET.get('classe', '')
    statut = request.GET.get('statut', 'actif')
    
    if search:
        eleves_qs = eleves_qs.filter(
            Q(nom__icontains=search) | 
            Q(prenom__icontains=search) | 
            Q(matricule__icontains=search)
        )
    if niveau_id:
        eleves_qs = eleves_qs.filter(niveau_id=niveau_id)
    if statut:
        eleves_qs = eleves_qs.filter(statut=statut)
    
    if annee:
        eleves_qs = eleves_qs.prefetch_related(
            Prefetch(
                'inscriptions',
                queryset=EleveInscription.objects.filter(annee_scolaire=annee).select_related('classe'),
                to_attr='current_inscriptions'
            )
        )
        classes_list = Classe.objects.filter(annee_scolaire=annee).order_by('niveau', 'nom', 'subdivision')
    else:
        classes_list = []
    
    paginator = Paginator(eleves_qs.distinct(), 30)
    page = request.GET.get('page')
    eleves = paginator.get_page(page)
    
    log_audit_helper(request.user, 'view', 'Eleve', None, 'Liste des élèves', request)
    return render(request, 'scolarite/eleve_list.html', {
        'eleves': eleves,
        'search': search,
        'niveau_filter': niveau_id,
        'statut_filter': statut,
        'classes_list': classes_list,
        'classe_filter': classe_id,
    })


@login_required
def eleve_create(request):
    if not request.user.has_module_permission('eleve_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de créer des élèves.")
        return redirect('scolarite:eleve_list')
    
    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES)
        if form.is_valid():
            eleve = form.save(commit=False)
            eleve.statut = Eleve.Statut.ACTIF
            eleve.save()
            
            annee_id = form.cleaned_data.get('annee_scolaire')
            classe = form.cleaned_data.get('classe')
            if annee_id and classe:
                EleveInscription.objects.create(
                    eleve=eleve,
                    classe=classe,
                    annee_scolaire=annee_id,
                )
            
            log_audit_helper(request.user, 'create', 'Eleve', eleve, f"Création de l'élève {eleve.nom_complet}", request)
            messages.success(request, f"L'élève {eleve.nom_complet} a été créé avec succès.")
            return redirect('scolarite:eleve_list')
    else:
        form = EleveForm()
    
    return render(request, 'scolarite/eleve_form.html', {
        'form': form,
        'eleve': None
    })


@login_required
def eleve_detail(request, pk):
    if not request.user.has_module_permission('eleve_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les élèves.")
        return redirect('dashboard')
    
    eleve = get_object_or_404(Eleve, pk=pk)
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    inscriptions = eleve.inscriptions.select_related('classe', 'annee_scolaire').order_by('-annee_scolaire__date_debut')
    current_inscription = inscriptions.filter(annee_scolaire=annee).first() if annee else None
    
    dossier_medical = None
    try:
        dossier_medical = eleve.dossier_medical
    except DossierMedical.DoesNotExist:
        pass
    
    documents = eleve.documents.all().order_by('-date_upload')
    disciplines = eleve.disciplines.all().order_by('-date_incident')[:10]
    
    log_audit_helper(request.user, 'view', 'Eleve', eleve, f"Détail de l'élève {eleve.nom_complet}", request)
    return render(request, 'scolarite/eleve_detail.html', {
        'eleve': eleve,
        'inscriptions': inscriptions,
        'current_inscription': current_inscription,
        'dossier_medical': dossier_medical,
        'documents': documents,
        'disciplines': disciplines,
    })


@login_required
def eleve_update(request, pk):
    if not request.user.has_module_permission('eleve_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des élèves.")
        return redirect('scolarite:eleve_list')
    
    eleve = get_object_or_404(Eleve, pk=pk)
    
    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES, instance=eleve)
        if form.is_valid():
            eleve_updated = form.save()
            log_audit_helper(request.user, 'update', 'Eleve', eleve_updated, f"Modification de l'élève {eleve_updated.nom_complet}", request)
            messages.success(request, f"L'élève {eleve_updated.nom_complet} a été modifié.")
            return redirect('scolarite:eleve_detail', pk=eleve.pk)
    else:
        form = EleveForm(instance=eleve)
    
    return render(request, 'scolarite/eleve_form.html', {
        'form': form,
        'eleve': eleve
    })


@login_required
def eleve_delete(request, pk):
    if not request.user.has_module_permission('eleve_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des élèves.")
        return redirect('scolarite:eleve_list')
    
    eleve = get_object_or_404(Eleve, pk=pk)
    
    if request.method == 'POST':
        log_audit_helper(request.user, 'delete', 'Eleve', eleve, f"Suppression de l'élève {eleve.nom_complet}", request)
        eleve.delete()
        messages.success(request, 'Élève supprimé.')
        return redirect('scolarite:eleve_list')
    
    return render(request, 'scolarite/eleve_confirm_delete.html', {'eleve': eleve})


@login_required
def parent_list(request):
    if not request.user.has_module_permission('eleve_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les parents.")
        return redirect('dashboard')
    
    parents = ParentTuteur.objects.select_related('eleve').order_by('-est_contact_principal', 'nom')
    search = request.GET.get('search', '')
    
    if search:
        parents = parents.filter(Q(nom__icontains=search) | Q(prenom__icontains=search))
    
    paginator = Paginator(parents, 20)
    page = request.GET.get('page')
    parents = paginator.get_page(page)
    
    return render(request, 'scolarite/parent_list.html', {'parents': parents, 'search': search})


@login_required
def parent_create(request, eleve_id=None):
    if not request.user.has_module_permission('eleve_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de créer des parents.")
        return redirect('scolarite:parent_list')
    
    eleve = None
    if eleve_id:
        eleve = get_object_or_404(Eleve, pk=eleve_id)
    
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        lien = request.POST.get('lien_parente')
        telephone = request.POST.get('telephone')
        eleve_id_post = request.POST.get('eleve')
        
        if eleve_id_post:
            eleve = get_object_or_404(Eleve, pk=eleve_id_post)
        
        if eleve and nom and prenom and lien and telephone:
            parent = ParentTuteur.objects.create(
                eleve=eleve,
                nom=nom,
                prenom=prenom,
                lien_parente=lien,
                telephone=telephone,
                est_contact_principal=request.POST.get('est_contact_principal') == 'on'
            )
            log_audit_helper(request.user, 'create', 'ParentTuteur', parent, f"Ajout du parent {parent} pour l'élève {eleve}", request)
            messages.success(request, f'Parent/Tuteur {parent} créé.')
            return redirect('scolarite:parent_list')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
    
    return render(request, 'scolarite/parent_form.html', {'parent': None, 'eleve': eleve})


@login_required
def dossiers_medical(request):
    if not request.user.has_module_permission('dossiers_medicaux', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les dossiers médicaux.")
        return redirect('dashboard')
    
    eleves = Eleve.objects.annotate(
        has_dossier=Count('dossier_medical')
    ).filter(has_dossier__gt=0).order_by('nom', 'prenom')[:100]
    
    return render(request, 'scolarite/dossiers_medical.html', {'eleves': eleves})


@login_required
def dossier_medical_edit(request, eleve_id):
    if not request.user.has_module_permission('dossiers_medicaux', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier les dossiers médicaux.")
        return redirect('scolarite:dossiers_medical')
    
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    dossier, created = DossierMedical.objects.get_or_create(eleve=eleve)
    
    if request.method == 'POST':
        dossier.groupe_sanguin = request.POST.get('groupe_sanguin', '')
        dossier.allergies = request.POST.get('allergies', '')
        dossier.traitements_en_cours = request.POST.get('traitements_en_cours', '')
        dossier.vaccinations = request.POST.get('vaccinations', '')
        dossier.maladies_chroniques = request.POST.get('maladies_chroniques', '')
        dossier.contacts_urgence_nom = request.POST.get('contacts_urgence_nom', '')
        dossier.contacts_urgence_tel = request.POST.get('contacts_urgence_tel', '')
        dossier.medecin_traitant = request.POST.get('medecin_traitant', '')
        dossier.observations = request.POST.get('observations', '')
        dossier.save()
        log_audit_helper(request.user, 'update', 'DossierMedical', dossier, f"Mise à jour du dossier médical de {eleve}", request)
        messages.success(request, 'Dossier médical mis à jour.')
        return redirect('scolarite:dossiers_medical')
    
    return render(request, 'scolarite/dossier_medical_form.html', {'dossier': dossier, 'eleve': eleve})


@login_required
def documents_eleve(request):
    if not request.user.has_module_permission('documents_eleve', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les documents.")
        return redirect('dashboard')
    
    documents = DocumentEleve.objects.select_related('eleve').order_by('-date_upload')
    search = request.GET.get('search', '')
    type_doc = request.GET.get('type', '')
    
    if search:
        documents = documents.filter(eleve__nom__icontains=search)
    if type_doc:
        documents = documents.filter(type_document=type_doc)
    
    paginator = Paginator(documents, 30)
    page = request.GET.get('page')
    documents = paginator.get_page(page)
    
    return render(request, 'scolarite/documents_eleve.html', {
        'documents': documents,
        'search': search,
        'type_doc': type_doc
    })


@login_required
def document_upload(request, eleve_id):
    if not request.user.has_module_permission('documents_eleve', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'uploader des documents.")
        return redirect('scolarite:documents_eleve')
    
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    
    if request.method == 'POST':
        type_doc = request.POST.get('type_document')
        fichier = request.FILES.get('fichier')
        description = request.POST.get('description', '')
        
        if fichier and type_doc:
            doc = DocumentEleve.objects.create(
                eleve=eleve,
                type_document=type_doc,
                fichier=fichier,
                description=description
            )
            log_audit_helper(request.user, 'create', 'DocumentEleve', doc, f"Upload document {type_doc} pour {eleve}", request)
            messages.success(request, 'Document uploadé.')
        
        return redirect('scolarite:eleve_detail', pk=eleve.pk)
    
    return render(request, 'scolarite/document_upload.html', {'eleve': eleve})


@login_required
def document_delete(request, pk):
    if not request.user.has_module_permission('documents_eleve', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des documents.")
        return redirect('scolarite:documents_eleve')
    
    document = get_object_or_404(DocumentEleve, pk=pk)
    
    if request.method == 'POST':
        log_audit_helper(request.user, 'delete', 'DocumentEleve', document, f"Suppression document {document.type_document} de {document.eleve}", request)
        document.delete()
        messages.success(request, 'Document supprimé.')
        return redirect('scolarite:documents_eleve')
    
    return render(request, 'scolarite/document_confirm_delete.html', {'document': document})


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir la discipline.")
        return redirect('dashboard')
    
    disciplines = SanctionRecompense.objects.select_related('eleve').order_by('-date_incident')
    
    search = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    statut_filter = request.GET.get('statut', '')
    
    if search:
        if search.isdigit():
            disciplines = disciplines.filter(eleve_id=int(search))
        else:
            disciplines = disciplines.filter(Q(eleve__nom__icontains=search) | Q(eleve__prenom__icontains=search))
    if type_filter:
        disciplines = disciplines.filter(type=type_filter)
    if statut_filter:
        disciplines = disciplines.filter(statut_traitement=statut_filter)
    
    paginator = Paginator(disciplines, 50)
    page = request.GET.get('page')
    disciplines = paginator.get_page(page)
    
    return render(request, 'scolarite/discipline_list.html', {
        'disciplines': disciplines,
        'search': search,
        'type_filter': type_filter,
        'statut_filter': statut_filter,
    })


@login_required
def discipline_create(request):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des sanctions.")
        return redirect('scolarite:discipline_list')
    
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve')
        type_discipline = request.POST.get('type')
        type_detail = request.POST.get('type_detail')
        description = request.POST.get('description')
        date_incident = request.POST.get('date_incident')
        points = int(request.POST.get('points', 0))
        
        eleve = get_object_or_404(Eleve, pk=eleve_id)
        
        obj = SanctionRecompense.objects.create(
            eleve=eleve,
            type=type_discipline,
            type_detail=type_detail,
            description=description,
            date_incident=date_incident,
            points=points,
            enregistre_par=request.user
        )
        
        log_audit_helper(request.user, 'create', 'SanctionRecompense', obj, f"Nouvelle {type_discipline} pour {eleve}", request)
        messages.success(request, 'Sanction/Récompense enregistrée.')
        return redirect('scolarite:discipline_list')
    
    return render(request, 'scolarite/discipline_form.html', {'discipline': None})


@login_required
def discipline_detail(request, pk):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir la discipline.")
        return redirect('dashboard')
    
    discipline = get_object_or_404(SanctionRecompense, pk=pk)
    return render(request, 'scolarite/discipline_detail.html', {'discipline': discipline})


@login_required
def discipline_edit(request, pk):
    if not request.user.has_module_permission('discipline', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des sanctions.")
        return redirect('scolarite:discipline_list')
    
    discipline = get_object_or_404(SanctionRecompense, pk=pk)
    
    if request.method == 'POST':
        discipline.type = request.POST.get('type')
        discipline.type_detail = request.POST.get('type_detail')
        discipline.description = request.POST.get('description')
        discipline.date_incident = request.POST.get('date_incident')
        discipline.points = int(request.POST.get('points', 0))
        discipline.save()
        log_audit_helper(request.user, 'update', 'SanctionRecompense', discipline, f"Modification {discipline.type} pour {discipline.eleve}", request)
        messages.success(request, 'Sanction/Récompense modifiée.')
        return redirect('scolarite:discipline_list')
    
    return render(request, 'scolarite/discipline_form.html', {'discipline': discipline})


@login_required
def discipline_delete(request, pk):
    if not request.user.has_module_permission('discipline', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des sanctions.")
        return redirect('scolarite:discipline_list')
    
    discipline = get_object_or_404(SanctionRecompense, pk=pk)
    
    if request.method == 'POST':
        log_audit_helper(request.user, 'delete', 'SanctionRecompense', discipline, f"Suppression {discipline.type} de {discipline.eleve}", request)
        discipline.delete()
        messages.success(request, 'Sanction/Récompense supprimée.')
        return redirect('scolarite:discipline_list')
    
    return render(request, 'scolarite/discipline_delete.html', {'discipline': discipline})


@login_required
def discipline_treat(request, pk):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de traiter des sanctions.")
        return redirect('scolarite:discipline_list')
    
    discipline = get_object_or_404(SanctionRecompense, pk=pk)
    
    if request.method == 'POST':
        discipline.statut_traitement = request.POST.get('statut_traitement', 'traite')
        discipline.traite_par = request.user
        discipline.date_traitement = datetime.now().date()
        discipline.save()
        log_audit_helper(request.user, 'update', 'SanctionRecompense', discipline, f"Traitement {discipline.type} pour {discipline.eleve}", request)
        messages.success(request, 'Sanction traitée.')
        return redirect('scolarite:discipline_list')
    
    return render(request, 'scolarite/discipline_treat.html', {'discipline': discipline})


@login_required
def discipline_statistics(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les statistiques.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    stats = SanctionRecompense.objects.aggregate(
        total=Count('id'),
        sanctions=Count('id', filter=Q(type='sanction')),
        recompenses=Count('id', filter=Q(type='recompense'))
    )
    
    return render(request, 'scolarite/discipline_statistics.html', {
        'stats': stats,
        'annee': annee
    })


@login_required
def discipline_history(request, eleve_id):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir l'historique.")
        return redirect('dashboard')
    
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    disciplines = eleve.disciplines.all().order_by('-date_incident')
    
    return render(request, 'scolarite/discipline_history.html', {
        'eleve': eleve,
        'disciplines': disciplines
    })


@login_required
def discipline_export(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation d'exporter les données.")
        return redirect('dashboard')
    
    disciplines = SanctionRecompense.objects.select_related('eleve').order_by('-date_incident')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="discipline_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Eleve', 'Type', 'Detail', 'Description', 'Points', 'Statut'])
    
    for d in disciplines:
        writer.writerow([
            d.date_incident,
            str(d.eleve),
            d.get_type_display(),
            d.type_detail,
            d.description,
            d.points,
            d.get_statut_traitement_display()
        ])
    
    return response


@login_required
def discipline_batch_treat(request):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de traiter des sanctions.")
        return redirect('scolarite:discipline_list')
    
    if request.method == 'POST':
        ids = request.POST.getlist('discipline_ids')
        statut = request.POST.get('statut_traitement', 'traite')
        
        updated = SanctionRecompense.objects.filter(pk__in=ids).update(
            statut_traitement=statut,
            traite_par=request.user,
            date_traitement=datetime.now().date()
        )
        
        log_audit_helper(request.user, 'update', 'SanctionRecompense', None, f"Traitement par lot de {updated} sanctions", request)
        messages.success(request, f'{updated} sanction(s) traitée(s).')
        return redirect('scolarite:discipline_list')
    
    return redirect('scolarite:discipline_list')


@login_required
def conduite_config_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir la configuration.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    configs = ConfigurationConduite.objects.filter(annee_scolaire=annee).order_by('niveau') if annee else []
    
    return render(request, 'scolarite/conduite_config_list.html', {
        'configs': configs,
        'annee': annee
    })


@login_required
def conduite_config_edit(request, niveau):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier la configuration.")
        return redirect('scolarite:conduite_config_list')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    config = ConfigurationConduite.objects.filter(annee_scolaire=annee, niveau_id=niveau).first()
    
    if not config and annee:
        from core.models import NiveauScolaire
        niveau_obj = get_object_or_404(NiveauScolaire, pk=niveau)
        config = ConfigurationConduite.objects.create(
            annee_scolaire=annee,
            niveau=niveau_obj,
            note_base=20.00,
            cree_par=request.user
        )
    
    if request.method == 'POST':
        config.note_base = request.POST.get('note_base', 20.00)
        config.save()
        log_audit_helper(request.user, 'update', 'ConfigurationConduite', config, f"Mise à jour config conduite pour {config.niveau}", request)
        messages.success(request, 'Configuration mise à jour.')
        return redirect('scolarite:conduite_config_list')
    
    return render(request, 'scolarite/conduite_config_form.html', {
        'config': config,
        'niveau_id': niveau
    })


@login_required
def periode_cloture_list(request):
    if not request.user.has_module_permission('periode_cloture', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les clôtures.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    if not profil_prof and not request.user.est_direction() and not request.user.est_superadmin():
        messages.error(request, "Accès restreint.")
        return redirect('dashboard')
    
    if profil_prof:
        classes = Classe.objects.filter(
            professeur_principal=profil_prof,
            annee_scolaire=annee
        ) if annee else []
    else:
        classes = Classe.objects.filter(annee_scolaire=annee) if annee else []
    
    classe_data = []
    from core.models import PeriodeEvaluation
    periodes = PeriodeEvaluation.objects.filter(annee_scolaire=annee) if annee else []
    
    for classe in classes:
        clotures = {}
        for p in periodes:
            cloture = CloturePeriode.objects.filter(classe=classe, periode=p).first()
            clotures[p.pk] = cloture
        classe_data.append({'classe': classe, 'clotures': clotures})
    
    return render(request, 'scolarite/periode_cloture_list.html', {
        'classe_data': classe_data,
        'periodes': periodes,
        'annee': annee
    })


@login_required
def periode_cloture_edit(request, classe_id):
    if not request.user.has_module_permission('periode_cloture', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de clôturer.")
        return redirect('scolarite:periode_cloture_list')
    
    classe = get_object_or_404(Classe, pk=classe_id)
    periode_id = request.POST.get('periode')
    from core.models import PeriodeEvaluation
    periode = get_object_or_404(PeriodeEvaluation, pk=periode_id)
    
    if request.method == 'POST':
        CloturePeriode.objects.update_or_create(
            classe=classe,
            periode=periode,
            defaults={'cloture_par': request.user}
        )
        log_audit_helper(request.user, 'update', 'CloturePeriode', None, f"Clôture de la période {periode} pour {classe}", request)
        messages.success(request, f'Période {periode} clôturée.')
    
    return redirect('scolarite:periode_cloture_list')


@login_required
def periode_cloture_delete(request, classe_id, periode_id):
    if not request.user.has_module_permission('periode_cloture', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer.")
        return redirect('scolarite:periode_cloture_list')
    
    cloture = CloturePeriode.objects.filter(classe_id=classe_id, periode_id=periode_id).first()
    
    if cloture and request.method == 'POST':
        log_audit_helper(request.user, 'delete', 'CloturePeriode', cloture, f"Annulation clôture période {cloture.periode} pour {cloture.classe}", request)
        cloture.delete()
        messages.success(request, 'Clôture supprimée.')
    
    return redirect('scolarite:periode_cloture_list')


@login_required
def note_cloture_list(request):
    if not request.user.has_module_permission('note_cloture', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les clôtures de notes.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    if not profil_prof:
        messages.error(request, "Vous n'êtes pas professeur.")
        return redirect('dashboard')
    
    from enseignement.models import Attribution
    attributions = Attribution.objects.filter(
        professeur=profil_prof,
        annee_scolaire=annee
    ).select_related('classe', 'matiere') if annee else []
    
    from core.models import PeriodeEvaluation
    periodes = PeriodeEvaluation.objects.filter(annee_scolaire=annee) if annee else []
    
    clotures_list = []
    for attr in attributions:
        for p in periodes:
            cloture = ClotureNotes.objects.filter(
                classe=attr.classe,
                professeur=profil_prof,
                periode=p
            ).first()
            clotures_list.append({
                'classe': attr.classe,
                'matiere': attr.matiere,
                'periode': p,
                'cloture': cloture
            })
    
    return render(request, 'scolarite/note_cloture_list.html', {
        'clotures_list': clotures_list,
        'annee': annee
    })


@login_required
def note_cloture_edit(request, classe_id):
    if not request.user.has_module_permission('note_cloture', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de clôturer les notes.")
        return redirect('scolarite:note_cloture_list')
    
    classe = get_object_or_404(Classe, pk=classe_id)
    periode_id = request.POST.get('periode_id')
    from core.models import PeriodeEvaluation
    periode = get_object_or_404(PeriodeEvaluation, pk=periode_id)
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    if request.method == 'POST' and periode and profil_prof:
        ClotureNotes.objects.update_or_create(
            classe=classe,
            professeur=profil_prof,
            periode=periode,
            defaults={'cloture_par': request.user}
        )
        log_audit_helper(request.user, 'update', 'ClotureNotes', None, f"Clôture des notes pour {classe} - {periode}", request)
        messages.success(request, 'Notes clôturées.')
    
    return redirect('scolarite:note_cloture_list')


@login_required
def annee_cloture_list(request):
    """Liste des clôtures d'année scolaire"""
    if not request.user.has_module_permission('annee_cloture', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les clôtures d'année.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    if not profil_prof and not request.user.est_direction() and not request.user.est_superadmin():
        messages.error(request, "Accès restreint.")
        return redirect('dashboard')
    
    if profil_prof:
        classes = Classe.objects.filter(
            professeur_principal=profil_prof,
            annee_scolaire=annee
        ) if annee else []
    else:
        classes = Classe.objects.filter(annee_scolaire=annee) if annee else []
    
    classe_data = []
    for classe in classes:
        cloture = ClotureAnneeScolaire.objects.filter(classe=classe, annee_scolaire=annee).first()
        classe_data.append({
            'classe': classe,
            'cloture': cloture
        })
    
    return render(request, 'scolarite/annee_cloture_list.html', {
        'classe_data': classe_data,
        'annee': annee
    })


@login_required
def annee_cloture_edit(request, classe_id):
    """Clôturer l'année scolaire pour une classe"""
    if not request.user.has_module_permission('annee_cloture', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de clôturer l'année.")
        return redirect('scolarite:annee_cloture_list')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    classe = get_object_or_404(Classe, pk=classe_id)
    profil_prof = getattr(request.user, 'profil_professeur', None)
    
    if profil_prof and classe.professeur_principal != profil_prof and not request.user.est_direction() and not request.user.est_superadmin():
        messages.error(request, "Vous n'êtes pas professeur principal de cette classe.")
        return redirect('scolarite:annee_cloture_list')
    
    if request.method == 'POST':
        from rapports.views import calculer_moyenne_generale, get_mention
        
        cloture, created = ClotureAnneeScolaire.objects.update_or_create(
            classe=classe,
            annee_scolaire=annee,
            defaults={
                'cloture_par': request.user,
                'est_validee': True
            }
        )
        
        inscriptions = EleveInscription.objects.filter(classe=classe, annee_scolaire=annee)
        
        for inscription in inscriptions:
            moyenne = calculer_moyenne_generale(inscription.eleve, classe, annee)
            inscription.moyenne_generale = moyenne
            
            if moyenne is not None:
                inscription.mention = get_mention(moyenne)
                if moyenne >= 10:
                    inscription.decision = 'Promu'
                else:
                    inscription.decision = 'Redouble'
            else:
                inscription.mention = ''
                inscription.decision = 'En attente'
            
            inscription.save()
        
        log_audit_helper(request.user, 'update', 'ClotureAnneeScolaire', cloture, f"Clôture année scolaire pour {classe}", request)
        messages.success(request, f'Année scolaire clôturée pour {classe}. {inscriptions.count()} élèves traités.')
        return redirect('scolarite:annee_cloture_list')
    
    return render(request, 'scolarite/annee_cloture_form.html', {
        'classe': classe,
        'annee': annee
    })


@login_required
def annee_cloture_delete(request, classe_id):
    """Annuler la clôture de l'année scolaire"""
    if not request.user.has_module_permission('annee_cloture', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation d'annuler la clôture.")
        return redirect('scolarite:annee_cloture_list')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    classe = get_object_or_404(Classe, pk=classe_id)
    cloture = ClotureAnneeScolaire.objects.filter(classe=classe, annee_scolaire=annee).first()
    
    if cloture and request.method == 'POST':
        log_audit_helper(request.user, 'delete', 'ClotureAnneeScolaire', cloture, f"Annulation clôture année {classe}", request)
        cloture.delete()
        
        EleveInscription.objects.filter(classe=classe, annee_scolaire=annee).update(
            moyenne_generale=None,
            mention='',
            decision=''
        )
        
        messages.success(request, 'Clôture d\'année annulée.')
    
    return redirect('scolarite:annee_cloture_list')


@login_required
def inscription_list(request):
    if not request.user.has_module_permission('inscriptions', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les inscriptions.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    inscriptions = EleveInscription.objects.select_related('eleve', 'classe', 'annee_scolaire').all()
    
    if annee:
        inscriptions = inscriptions.filter(annee_scolaire=annee)
    
    search = request.GET.get('search', '')
    if search:
        inscriptions = inscriptions.filter(
            Q(eleve__nom__icontains=search) |
            Q(eleve__prenom__icontains=search) |
            Q(eleve__matricule__icontains=search)
        )
    
    inscriptions = inscriptions.order_by('-date_inscription')
    
    return render(request, 'scolarite/inscription_list.html', {
        'inscriptions': inscriptions,
        'annee': annee,
        'search': search
    })


@login_required
def cloture_annee_globale(request):
    """Clôture globale de l'année scolaire par la Direction"""
    if not request.user.est_direction() and not request.user.est_superadmin():
        messages.error(request, "Accès réservé à la Direction.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    if not annee:
        messages.error(request, "Aucune année scolaire active.")
        return redirect('dashboard')
    
    classes = Classe.objects.filter(annee_scolaire=annee)
    
    classe_stats = []
    toutes_cloturees = True
    total_nb = 0
    total_promus = 0
    total_redoublants = 0
    
    for classe in classes:
        cloture_prof = ClotureAnneeScolaire.objects.filter(classe=classe, annee_scolaire=annee).first()
        
        inscriptions = EleveInscription.objects.filter(classe=classe, annee_scolaire=annee)
        promus = inscriptions.filter(decision='Promu').count()
        redoublants = inscriptions.filter(decision='Redouble').count()
        
        total_nb += inscriptions.count()
        total_promus += promus
        total_redoublants += redoublants
        
        if not cloture_prof or not cloture_prof.est_validee:
            toutes_cloturees = False
        
        classe_stats.append({
            'classe': classe,
            'cloture_prof': cloture_prof,
            'nb_inscriptions': inscriptions.count(),
            'promus': promus,
            'redoublants': redoublants
        })
    
    if request.method == 'POST' and toutes_cloturees:
        action = request.POST.get('action', '')
        
        from core.models import NiveauScolaire
        
        reinscriptions_count = 0
        for classe in classes:
            inscriptions = EleveInscription.objects.filter(classe=classe, annee_scolaire=annee, decision='Promu')
            
            niveau = classe.niveau
            classe_actuelle_numero = getattr(niveau, 'ordre', 0)
            nextNiveau = NiveauScolaire.objects.filter(
                annee_scolaire=annee,
                ordre=classe_actuelle_numero + 1
            ).first()
            
            nouvelle_classe = None
            if nextNiveau:
                nouvelle_classe = Classe.objects.filter(
                    niveau=nextNiveau,
                    subdivision=classe.subdivision,
                    annee_scolaire=annee
                ).first()
            
            for inscription in inscriptions:
                if nouvelle_classe:
                    EleveInscription.objects.create(
                        eleve=inscription.eleve,
                        classe=nouvelle_classe,
                        annee_scolaire=annee
                    )
                    reinscriptions_count += 1
                else:
                    EleveInscription.objects.create(
                        eleve=inscription.eleve,
                        classe=classe,
                        annee_scolaire=annee
                    )
                    reinscriptions_count += 1
        
        if action == 'fermer':
            annee.est_active = False
            annee.save()
            log_audit_helper(request.user, 'update', 'AnneeScolaire', annee, f"Année {annee} fermée", request)
            messages.success(request, f'Année scolaire {annee} fermée. {reinscriptions_count} élèves promus ont été réinscrits.')
        else:
            messages.success(request, f'{reinscriptions_count} élèves promus ont été réinscrits.')
        
        return redirect('dashboard')
    
    return render(request, 'scolarite/cloture_annee_globale.html', {
        'annee': annee,
        'classe_stats': classe_stats,
        'toutes_cloturees': toutes_cloturees,
        'total_nb': total_nb,
        'total_promus': total_promus,
        'total_redoublants': total_redoublants
    })
