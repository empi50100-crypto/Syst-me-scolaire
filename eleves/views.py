from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q, Count
from django.http import HttpResponse
from datetime import datetime
import csv

from eleves.models import (
    Eleve, ParentTuteur, DossierMedical, DocumentEleve,
    PeriodeCloture, NotePeriodeCloture, DisciplineEleve,
    Inscription, ConduiteConfig, ConduiteEleve
)
from eleves.forms import EleveForm, DocumentFormSet
from finances.models import AnneeScolaire
from academics.models import Classe
from authentification.models import DemandeApprobation, Notification, User


def log_audit(user, action, model_type, obj, details, request):
    try:
        from audit.models import AuditLog
        AuditLog.objects.create(
            user=user,
            action=action,
            model_type=model_type,
            object_id=obj.pk if obj else None,
            details=details,
            ip_address=request.META.get('REMOTE_ADDR', '')
        )
    except:
        pass


@login_required
def eleve_list(request):
    if not request.user.has_module_permission('eleve_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les eleves.")
        return redirect('dashboard')
    
    eleves_qs = Eleve.objects.all().order_by('nom', 'prenom')
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    search = request.GET.get('search', '')
    niveau = request.GET.get('niveau', '')
    classe_id = request.GET.get('classe', '')
    statut = request.GET.get('statut', 'actif')
    
    if search:
        eleves_qs = eleves_qs.filter(
            Q(nom__icontains=search) | 
            Q(prenom__icontains=search) | 
            Q(matricule__icontains=search)
        )
    if niveau:
        eleves_qs = eleves_qs.filter(niveau=niveau)
    if statut:
        eleves_qs = eleves_qs.filter(statut=statut)
    
    if annee:
        eleves_qs = eleves_qs.prefetch_related(
            Prefetch(
                'inscriptions',
                queryset=Inscription.objects.filter(annee_scolaire=annee).select_related('classe'),
                to_attr='current_inscriptions'
            )
        )
        classes_list = Classe.objects.filter(annee_scolaire=annee).order_by('niveau', 'nom', 'subdivision')
    else:
        classes_list = []
    
    paginator = Paginator(eleves_qs.distinct(), 30)
    page = request.GET.get('page')
    eleves = paginator.get_page(page)
    
    log_audit(request.user, 'view', 'Eleve', None, 'Liste des eleves', request)
    return render(request, 'eleves/eleve_list.html', {
        'eleves': eleves,
        'search': search,
        'niveau_filter': niveau,
        'statut_filter': statut,
        'classes_list': classes_list,
        'classe_filter': classe_id,
    })


@login_required
def eleve_create(request):
    if not request.user.has_module_permission('eleve_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de creer des eleves.")
        return redirect('eleves:eleve_list')
    
    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES)
        if form.is_valid():
            eleve = form.save(commit=False)
            eleve.statut = Eleve.Statut.ACTIF
            
            is_direction = request.user.is_direction() or request.user.is_superadmin()
            
            if not is_direction:
                details_apos = f"""Etat propose:
- Nom: {eleve.nom}
- Prenom: {eleve.prenom}
- Date de naissance: {eleve.date_naissance}
- Sexe: {eleve.get_sexe_display()}"""
                
                demande = DemandeApprobation.objects.create(
                    demandeur=request.user,
                    type_action=DemandeApprobation.TypeAction.CREATION,
                    type_objet=DemandeApprobation.TypeObjet.ELEVE,
                    objet_repr=str(eleve),
                    details=f"Demande de creation de l'eleve {eleve.nom_complet}",
                    details_apos=details_apos
                )
                
                messages.success(request, 'Votre demande a ete soumise pour approbation.')
                return redirect('eleves:eleve_list')
            
            eleve.save()
            
            messages.success(request, f"L'eleve {eleve.nom_complet} a ete cree avec succes.")
            return redirect('eleves:eleve_list')
    else:
        form = EleveForm()
    
    return render(request, 'eleves/eleve_form.html', {
        'form': form,
        'eleve': None
    })


@login_required
def eleve_detail(request, pk):
    if not request.user.has_module_permission('eleve_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les eleves.")
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
    
    return render(request, 'eleves/eleve_detail.html', {
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
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des eleves.")
        return redirect('eleves:eleve_list')
    
    eleve = get_object_or_404(Eleve, pk=pk)
    
    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES, instance=eleve)
        if form.is_valid():
            eleve_updated = form.save(commit=False)
            eleve_updated.save()
            messages.success(request, f"L'eleve {eleve_updated.nom_complet} a ete modifie.")
            return redirect('eleves:eleve_detail', pk=eleve.pk)
    else:
        form = EleveForm(instance=eleve)
    
    return render(request, 'eleves/eleve_form.html', {
        'form': form,
        'eleve': eleve
    })


@login_required
def eleve_delete(request, pk):
    if not request.user.has_module_permission('eleve_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des eleves.")
        return redirect('eleves:eleve_list')
    
    eleve = get_object_or_404(Eleve, pk=pk)
    
    if request.method == 'POST':
        eleve.delete()
        messages.success(request, 'Eleve supprime.')
        return redirect('eleves:eleve_list')
    
    return render(request, 'eleves/eleve_confirm_delete.html', {'eleve': eleve})


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
    
    return render(request, 'eleves/parent_list.html', {'parents': parents, 'search': search})


@login_required
def parent_create(request, eleve_id=None):
    if not request.user.has_module_permission('eleve_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de creer des parents.")
        return redirect('eleves:parent_list')
    
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
            messages.success(request, f'Parent/Tuteur {parent} cree.')
            return redirect('eleves:parent_list')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
    
    return render(request, 'eleves/parent_form.html', {'parent': None, 'eleve': eleve})


@login_required
def dossiers_medical(request):
    if not request.user.has_module_permission('dossiers_medicaux', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les dossiers medicaux.")
        return redirect('dashboard')
    
    eleves = Eleve.objects.annotate(
        has_dossier=Count('dossier_medical')
    ).filter(has_dossier__gt=0).order_by('nom', 'prenom')[:100]
    
    return render(request, 'eleves/dossiers_medical.html', {'eleves': eleves})


@login_required
def dossier_medical_edit(request, eleve_id):
    if not request.user.has_module_permission('dossiers_medicaux', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier les dossiers medicaux.")
        return redirect('eleves:dossiers_medical')
    
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
        messages.success(request, 'Dossier medical mis a jour.')
        return redirect('eleves:dossiers_medical')
    
    return render(request, 'eleves/dossier_medical_form.html', {'dossier': dossier, 'eleve': eleve})


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
    
    return render(request, 'eleves/documents_eleve.html', {
        'documents': documents,
        'search': search,
        'type_doc': type_doc
    })


@login_required
def document_upload(request, eleve_id):
    if not request.user.has_module_permission('documents_eleve', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'uploader des documents.")
        return redirect('eleves:documents_eleve')
    
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    
    if request.method == 'POST':
        type_doc = request.POST.get('type_document')
        fichier = request.FILES.get('fichier')
        description = request.POST.get('description', '')
        
        if fichier and type_doc:
            DocumentEleve.objects.create(
                eleve=eleve,
                type_document=type_doc,
                fichier=fichier,
                description=description
            )
            messages.success(request, 'Document uploade.')
        
        return redirect('eleves:eleve_detail', pk=eleve.pk)
    
    return render(request, 'eleves/document_upload.html', {'eleve': eleve})


@login_required
def document_delete(request, pk):
    if not request.user.has_module_permission('documents_eleve', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des documents.")
        return redirect('eleves:documents_eleve')
    
    document = get_object_or_404(DocumentEleve, pk=pk)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document supprime.')
        return redirect('eleves:documents_eleve')
    
    return render(request, 'eleves/document_confirm_delete.html', {'document': document})


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir la discipline.")
        return redirect('dashboard')
    
    disciplines = DisciplineEleve.objects.select_related('eleve').order_by('-date_incident')
    
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
    
    return render(request, 'eleves/discipline_list.html', {
        'disciplines': disciplines,
        'search': search,
        'type_filter': type_filter,
        'statut_filter': statut_filter,
    })


@login_required
def discipline_create(request):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des sanctions.")
        return redirect('eleves:discipline_list')
    
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve')
        type_discipline = request.POST.get('type')
        type_detail = request.POST.get('type_detail')
        description = request.POST.get('description')
        date_incident = request.POST.get('date_incident')
        points = int(request.POST.get('points', 0))
        
        eleve = get_object_or_404(Eleve, pk=eleve_id)
        
        DisciplineEleve.objects.create(
            eleve=eleve,
            type=type_discipline,
            type_detail=type_detail,
            description=description,
            date_incident=date_incident,
            points=points,
            enregistre_par=request.user
        )
        
        messages.success(request, 'Sanction/Récompense enregistrée.')
        return redirect('eleves:discipline_list')
    
    return render(request, 'eleves/discipline_form.html', {'discipline': None})


@login_required
def discipline_detail(request, pk):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir la discipline.")
        return redirect('dashboard')
    
    discipline = get_object_or_404(DisciplineEleve, pk=pk)
    return render(request, 'eleves/discipline_detail.html', {'discipline': discipline})


@login_required
def discipline_edit(request, pk):
    if not request.user.has_module_permission('discipline', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des sanctions.")
        return redirect('eleves:discipline_list')
    
    discipline = get_object_or_404(DisciplineEleve, pk=pk)
    
    if request.method == 'POST':
        discipline.type = request.POST.get('type')
        discipline.type_detail = request.POST.get('type_detail')
        discipline.description = request.POST.get('description')
        discipline.date_incident = request.POST.get('date_incident')
        discipline.points = int(request.POST.get('points', 0))
        discipline.save()
        messages.success(request, 'Sanction/Récompense modifiée.')
        return redirect('eleves:discipline_list')
    
    return render(request, 'eleves/discipline_form.html', {'discipline': discipline})


@login_required
def discipline_delete(request, pk):
    if not request.user.has_module_permission('discipline', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des sanctions.")
        return redirect('eleves:discipline_list')
    
    discipline = get_object_or_404(DisciplineEleve, pk=pk)
    
    if request.method == 'POST':
        discipline.delete()
        messages.success(request, 'Sanction/Récompense supprimée.')
        return redirect('eleves:discipline_list')
    
    return render(request, 'eleves/discipline_confirm_delete.html', {'discipline': discipline})


@login_required
def discipline_treat(request, pk):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de traiter des sanctions.")
        return redirect('eleves:discipline_list')
    
    discipline = get_object_or_404(DisciplineEleve, pk=pk)
    
    if request.method == 'POST':
        discipline.statut_traitement = request.POST.get('statut_traitement', 'traite')
        discipline.traite_par = request.user
        discipline.date_traitement = datetime.now().date()
        discipline.save()
        messages.success(request, 'Sanction traitée.')
        return redirect('eleves:discipline_list')
    
    return render(request, 'eleves/discipline_treat.html', {'discipline': discipline})


@login_required
def discipline_statistics(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les statistiques.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    stats = DisciplineEleve.objects.aggregate(
        total=Count('id'),
        sanctions=Count('id', filter=Q(type='sanction')),
        recompenses=Count('id', filter=Q(type='recompense'))
    )
    
    return render(request, 'eleves/discipline_statistics.html', {
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
    
    return render(request, 'eleves/discipline_history.html', {
        'eleve': eleve,
        'disciplines': disciplines
    })


@login_required
def discipline_export(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation d'exporter les données.")
        return redirect('dashboard')
    
    disciplines = DisciplineEleve.objects.select_related('eleve').order_by('-date_incident')
    
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
        return redirect('eleves:discipline_list')
    
    if request.method == 'POST':
        ids = request.POST.getlist('discipline_ids')
        statut = request.POST.get('statut_traitement', 'traite')
        
        updated = DisciplineEleve.objects.filter(pk__in=ids).update(
            statut_traitement=statut,
            traite_par=request.user,
            date_traitement=datetime.now().date()
        )
        
        messages.success(request, f'{updated} sanction(s) traitee(s).')
        return redirect('eleves:discipline_list')
    
    return redirect('eleves:discipline_list')


@login_required
def conduite_config_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir la configuration.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    configs = ConduiteConfig.objects.filter(annee_scolaire=annee).order_by('niveau') if annee else []
    
    return render(request, 'eleves/conduite_config_list.html', {
        'configs': configs,
        'annee': annee
    })


@login_required
def conduite_config_edit(request, niveau):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier la configuration.")
        return redirect('eleves:conduite_config_list')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    config = ConduiteConfig.objects.filter(annee_scolaire=annee, niveau=niveau).first()
    
    if not config and annee:
        config = ConduiteConfig.objects.create(
            annee_scolaire=annee,
            niveau=niveau,
            note_base=20.00,
            cree_par=request.user
        )
    
    if request.method == 'POST':
        config.note_base = request.POST.get('note_base', 20.00)
        config.save()
        messages.success(request, 'Configuration mise a jour.')
        return redirect('eleves:conduite_config_list')
    
    return render(request, 'eleves/conduite_config_form.html', {
        'config': config,
        'niveau': niveau
    })


@login_required
def periode_cloture_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les clotures.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    if not hasattr(request.user, 'professeur') or not request.user.professeur:
        messages.error(request, "Vous n'etes pas professeur principal.")
        return redirect('dashboard')
    
    classes = Classe.objects.filter(
        professeur_principal=request.user.professeur,
        annee_scolaire=annee
    ) if annee else []
    
    if not classes.exists() and not request.user.is_direction() and not request.user.is_superadmin():
        messages.error(request, "Vous n'etes pas professeur principal.")
        return redirect('dashboard')
    
    if request.user.is_direction() or request.user.is_superadmin():
        classes = Classe.objects.filter(annee_scolaire=annee) if annee else []
    
    classe_data = []
    for classe in classes:
        clotures = {}
        for p in [1, 2, 3]:
            cloture = PeriodeCloture.objects.filter(classe=classe, periode=p).first()
            clotures[p] = cloture
        classe_data.append({'classe': classe, 'clotures': clotures})
    
    return render(request, 'eleves/periode_cloture_list.html', {
        'classe_data': classe_data,
        'annee': annee
    })


@login_required
def periode_cloture_edit(request, classe_id):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de cloturer.")
        return redirect('eleves:periode_cloture_list')
    
    classe = get_object_or_404(Classe, pk=classe_id)
    periode = int(request.POST.get('periode', 1))
    
    if request.method == 'POST':
        PeriodeCloture.objects.update_or_create(
            classe=classe,
            periode=periode,
            defaults={'cloture_par': request.user}
        )
        messages.success(request, f'Periode {periode} cloturee.')
    
    return redirect('eleves:periode_cloture_list')


@login_required
def periode_cloture_delete(request, classe_id, periode):
    if not request.user.has_module_permission('discipline', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer.")
        return redirect('eleves:periode_cloture_list')
    
    cloture = PeriodeCloture.objects.filter(classe_id=classe_id, periode=periode).first()
    
    if cloture and request.method == 'POST':
        cloture.delete()
        messages.success(request, 'Cloture supprimee.')
    
    return redirect('eleves:periode_cloture_list')


@login_required
def note_cloture_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les clotures de notes.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    if not hasattr(request.user, 'professeur') or not request.user.professeur:
        messages.error(request, "Vous n'etes pas professeur.")
        return redirect('dashboard')
    
    from academics.models import Enseignement
    enseignements = Enseignement.objects.filter(
        professeur=request.user.professeur,
        classe__annee_scolaire=annee
    ).select_related('classe', 'matiere') if annee else []
    
    clotures_list = []
    for ens in enseignements:
        for p in [1, 2, 3]:
            cloture = NotePeriodeCloture.objects.filter(
                classe=ens.classe,
                professeur=request.user.professeur,
                periode=p
            ).first()
            clotures_list.append({
                'classe': ens.classe,
                'matiere': ens.matiere,
                'periode': p,
                'cloture': cloture
            })
    
    return render(request, 'eleves/note_cloture_list.html', {
        'clotures_list': clotures_list,
        'annee': annee
    })


@login_required
def note_cloture_edit(request, classe_id):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation de cloturer les notes.")
        return redirect('eleves:note_cloture_list')
    
    from academics.models import Matiere
    classe = get_object_or_404(Classe, pk=classe_id)
    matiere_id = request.POST.get('matiere_id')
    periode = int(request.POST.get('periode', 1))
    professeur = getattr(request.user, 'professeur', None)
    
    if request.method == 'POST' and matiere_id and professeur:
        NotePeriodeCloture.objects.update_or_create(
            classe=classe,
            professeur=professeur,
            periode=periode
        )
        messages.success(request, 'Notes cloturees.')
    
    return redirect('eleves:note_cloture_list')
