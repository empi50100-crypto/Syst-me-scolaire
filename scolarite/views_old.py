from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Eleve, Inscription, ParentTuteur, DossierMedical, DocumentEleve, DisciplineEleve, ConduiteConfig, ConduiteEleve, PeriodeCloture, NotePeriodeCloture
from .forms import EleveForm, DocumentForm
from finances.models import AnneeScolaire
from accounts.models import log_audit, DemandeApprobation, Notification, User


def is_direction_or_secretaire(user):
    return user.is_authenticated and (user.is_direction() or user.is_secretaire() or user.is_superadmin())


def is_surveillance_or_direction_or_admin(user):
    return user.is_authenticated and (user.is_surveillance() or user.is_direction() or user.is_superadmin())


def is_prof_or_surveillance_or_direction(user):
    return user.is_authenticated and (user.is_professeur() or user.is_surveillance() or user.is_direction() or user.is_superadmin())


@login_required
def eleve_list(request):
    if not request.user.has_module_permission('eleve_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les élèves.")
        return redirect('dashboard')
    
    from finances.models import AnneeScolaire
    from enseignement.models import Classe
    from django.db.models import Prefetch, Q
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    eleves_qs = Eleve.objects.all().order_by('nom', 'prenom')
    
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
    if classe_id:
        eleves_qs = eleves_qs.filter(inscriptions__classe_id=classe_id, inscriptions__annee_scolaire=annee)
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

    log_audit(request.user, 'view', 'Eleve', None, 'Liste des élèves', request)
    return render(request, 'scolarite/eleve_list.html', {
        'eleves': eleves,
        'search': search,
        'niveau_filter': niveau,
        'classe_filter': classe_id,
        'statut_filter': statut,
        'niveaux': Eleve.Niveau.choices,
        'classes': classes_list,
        'statuts': Eleve.Statut.choices,
    })


@login_required
def eleve_list(request):
    if not request.user.has_module_permission('eleve_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les détails d'un élève.")
        return redirect('scolarite:eleve_list')
    
    eleve = get_object_or_404(Eleve, pk=pk)
    inscriptions = eleve.inscriptions.select_related('classe', 'annee_scolaire').order_by('-annee_scolaire__date_debut')
    log_audit(request.user, 'view', 'Eleve', eleve, f'Consultation fiche élève', request)
    return render(request, 'scolarite/eleve_detail.html', {'eleve': eleve, 'inscriptions': inscriptions})


@login_required
def eleve_list(request):
    if not request.user.has_module_permission('eleve_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'ajouter des élèves.")
        return redirect('scolarite:eleve_list')
    
    from .forms import DocumentFormSet
    
    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES)
        document_formset = DocumentFormSet(request.POST, request.FILES)
        
        if form.is_valid():
            eleve = form.save(commit=False)
            
            if request.user.is_superadmin() or request.user.is_direction():
                eleve.save()
                
                print("Processing documents...")
                print("Form is valid:", form.is_valid())
                print("Formset is valid:", document_formset.is_valid())
                print("Number of forms in formset:", len(document_formset))
                
                for i, doc_form in enumerate(document_formset):
                    print(f"=== Form {i} ===")
                    print(f"Has changed: {doc_form.has_changed()}")
                    print(f"Errors: {doc_form.errors}")
                    if not doc_form.is_valid():
                        print("Doc form errors:", doc_form.errors)
                        continue
                    doc_data = doc_form.cleaned_data
                    print(f"Cleaned data: {doc_data}")
                    
                    if not doc_data:
                        continue
                    
                    fichier = doc_data.get('fichier')
                    type_doc = doc_data.get('type_document')
                    description = doc_data.get('description', '')
                    
                    print(f"Form {i}: fichier={fichier}, type_doc={type_doc}")
                    
                    if fichier and type_doc:
                        existing_doc = DocumentEleve.objects.filter(
                            eleve=eleve, 
                            type_document=type_doc
                        ).first()
                        
                        if existing_doc:
                            messages.error(request, f'Un document de type "{existing_doc.get_type_document_display()}" existe déjà pour cet élève.')
                        else:
                            doc = DocumentEleve.objects.create(
                                eleve=eleve,
                                type_document=type_doc,
                                fichier=fichier,
                                description=description
                            )
                            print(f"Document created: {doc}")
                
                log_audit(request.user, 'create', 'Eleve', eleve, f'Création élève: {eleve.nom_complet}', request)
                messages.success(request, f'L\'élève {eleve.nom_complet} a été créé avec succès.')
                return redirect('scolarite:eleve_list')
            else:
                details_apos = f"""État proposé:
- Nom: {eleve.nom}
- Prénom: {eleve.prenom}
- Date de naissance: {eleve.date_naissance}
- Lieu de naissance: {eleve.lieu_naissance}
- Sexe: {eleve.get_sexe_display()}
- Adresse: {eleve.adresse}
- Téléphone parent: {eleve.telephone_parent}
- Email parent: {eleve.email_parent}
- Statut: {eleve.get_statut_display()}"""
                
                demande = DemandeApprobation.objects.create(
                    demandeur=request.user,
                    type_action=DemandeApprobation.TypeAction.CREATION,
                    type_objet=DemandeApprobation.TypeObjet.ELEVE,
                    objet_repr=str(eleve),
                    details=f"Demande de création de l'élève {eleve.nom_complet}",
                    details_apos=details_apos
                )
                
                from accounts.models import Notification, User
                approbateurs = User.objects.filter(role__in=[User.Role.SUPERADMIN, User.Role.DIRECTION], is_active=True)
                for approbateur in approbateurs:
                    Notification.creer_notification(
                        destinataire=approbateur,
                        type_notification=Notification.TypeNotification.AUTRE,
                        titre="Demande d'approbation - Création élève",
                        message=f"{request.user.get_full_name() or request.user.username} demande la création de l'élève: {eleve.nom_complet}",
                        expediteur=request.user,
                        lien='/authentification/demandes/'
                    )
                
                messages.success(request, 'Votre demande de création a été soumise pour approbation.')
        return redirect('scolarite:eleve_list')
    else:
        form = EleveForm()
        document_formset = DocumentFormSet()
    
    return render(request, 'scolarite/eleve_form.html', {
        'form': form, 
        'document_formset': document_formset,
        'action': 'Créer'
    })


@login_required
def eleve_list(request):
    if not request.user.has_module_permission('eleve_list', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier des élèves.")
        return redirect('scolarite:eleve_list')
    
    from .forms import DocumentFormSet
    eleve = get_object_or_404(Eleve, pk=pk)
    
    details_avant = f"""État actuel de l'élève:
- Nom: {eleve.nom}
- Prénom: {eleve.prenom}
- Date de naissance: {eleve.date_naissance}
- Lieu de naissance: {eleve.lieu_naissance}
- Sexe: {eleve.get_sexe_display()}
- Adresse: {eleve.adresse}
- Téléphone parent: {eleve.telephone_parent}
- Email parent: {eleve.email_parent}
- Statut: {eleve.get_statut_display()}"""
    
    if request.method == 'POST':
        form = EleveForm(request.POST, request.FILES, instance=eleve)
        document_formset = DocumentFormSet(request.POST, request.FILES)
        
        if form.is_valid():
            eleve_updated = form.save(commit=False)
            
            if request.user.is_superadmin() or request.user.is_direction():
                eleve_updated.save()
                print("=== Processing documents in update ===")
                print("Total forms:", len(document_formset))
                
                for i, doc_form in enumerate(document_formset):
                    print(f"=== Form {i} ===")
                    print(f"Has changed: {doc_form.has_changed()}")
                    print(f"Errors: {doc_form.errors}")
                    if not doc_form.is_valid():
                        print("Doc form errors:", doc_form.errors)
                        continue
                    doc_data = doc_form.cleaned_data
                    print(f"Cleaned data: {doc_data}")
                    
                    if not doc_data:
                        continue
                    
                    fichier = doc_data.get('fichier')
                    type_doc = doc_data.get('type_document')
                    description = doc_data.get('description', '')
                    
                    print(f"Form {i}: fichier={fichier}, type_doc={type_doc}")
                    
                    if fichier and type_doc:
                        existing_doc = DocumentEleve.objects.filter(
                            eleve=eleve, 
                            type_document=type_doc
                        ).first()
                        
                        if existing_doc:
                            messages.error(request, f'Un document de type "{existing_doc.get_type_document_display()}" existe déjà pour cet élève.')
                        else:
                            doc = DocumentEleve.objects.create(
                                eleve=eleve,
                                type_document=type_doc,
                                fichier=fichier,
                                description=description
                            )
                            print(f"Document created: {doc}")
                
                log_audit(request.user, 'update', 'Eleve', eleve_updated, f'Modification élève: {eleve_updated.nom_complet}', request)
                messages.success(request, f'L\'élève {eleve_updated.nom_complet} a été modifié avec succès.')
                return redirect('scolarite:eleve_detail', pk=eleve.pk)
            
            details_apos = f"""État proposé:
- Nom: {eleve_updated.nom}
- Prénom: {eleve_updated.prenom}
- Date de naissance: {eleve_updated.date_naissance}
- Lieu de naissance: {eleve_updated.lieu_naissance}
- Sexe: {eleve_updated.get_sexe_display()}
- Adresse: {eleve_updated.adresse}
- Téléphone parent: {eleve_updated.telephone_parent}
- Email parent: {eleve_updated.email_parent}
- Statut: {eleve_updated.get_statut_display()}"""
            
            demande = DemandeApprobation.objects.create(
                demandeur=request.user,
                type_action=DemandeApprobation.TypeAction.MODIFICATION,
                type_objet=DemandeApprobation.TypeObjet.ELEVE,
                objet_id=eleve.pk,
                objet_repr=str(eleve),
                details=f"Demande de modification de l'élève {eleve.nom_complet}",
                details_avant=details_avant,
                details_apos=details_apos
            )
            
            from accounts.models import Notification, User
            approbateurs = User.objects.filter(role__in=[User.Role.SUPERADMIN, User.Role.DIRECTION], is_active=True)
            for approbateur in approbateurs:
                Notification.creer_notification(
                    destinataire=approbateur,
                    type_notification=Notification.TypeNotification.AUTRE,
                    titre="Demande d'approbation - Modification élève",
                    message=f"{request.user.get_full_name() or request.user.username} demande la modification de l'élève: {eleve.nom_complet}",
                    expediteur=request.user,
                    lien='/authentification/demandes/'
                )
            
            messages.success(request, 'Votre demande de modification a été soumise pour approbation.')
        return redirect('scolarite:eleve_detail', pk=eleve.pk)
    else:
        form = EleveForm(instance=eleve)
        document_formset = DocumentFormSet()
    return render(request, 'scolarite/eleve_form.html', {
        'form': form, 
        'document_formset': document_formset,
        'eleve': eleve, 
        'action': 'Modifier'
    })


def is_direction_or_admin(user):
    return user.is_authenticated and (user.is_direction() or user.is_superadmin())


@login_required
def eleve_list(request):
    if not request.user.has_module_permission('eleve_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des élèves.")
        return redirect('scolarite:eleve_list')
    
    eleve = get_object_or_404(Eleve, pk=pk)
    
    if request.user.is_superadmin() or request.user.is_direction():
        eleve.statut = 'supprime'
        eleve.save()
        log_audit(request.user, 'delete', 'Eleve', eleve, f'Suppression élève: {eleve.nom_complet}', request)
        messages.success(request, f'L\'élève {eleve.nom_complet} a été supprimé.')
        return redirect('scolarite:eleve_list')
    
    details = f"Demande de suppression de l'élève: {eleve.nom_complet}"
    
    demande = DemandeApprobation.objects.create(
        demandeur=request.user,
        type_action=DemandeApprobation.TypeAction.SUPPRESSION,
        type_objet=DemandeApprobation.TypeObjet.ELEVE,
        objet_id=eleve.pk,
        objet_repr=str(eleve),
        details=details,
        details_apos=details
    )
    
    from accounts.models import Notification, User
    approbateurs = User.objects.filter(role__in=[User.Role.SUPERADMIN, User.Role.DIRECTION], is_active=True)
    for approbateur in approbateurs:
        Notification.creer_notification(
            destinataire=approbateur,
            type_notification=Notification.TypeNotification.AUTRE,
            titre="Demande d'approbation - Suppression élève",
            message=f"{request.user.get_full_name() or request.user.username} demande la suppression de l'élève: {eleve.nom_complet}",
            expediteur=request.user,
            lien='/authentification/demandes/'
        )
    
    messages.success(request, 'Votre demande de suppression a été soumise pour approbation.')
    return redirect('scolarite:eleve_list')


# ==================== Parents/Tuteurs ====================
@login_required
def parent_list_view(request):
    if not request.user.has_module_permission('eleve_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les parents.")
        return redirect('dashboard')
    
    parents = ParentTuteur.objects.select_related('eleve').order_by('-est_contact_principal', 'nom')
    search = request.GET.get('search', '')
    if search:
        parents = parents.filter(nom__icontains=search, prenom__icontains=search)
    paginator = Paginator(parents, 20)
    page = request.GET.get('page')
    parents = paginator.get_page(page)
    return render(request, 'scolarite/parent_list.html', {'parents': parents, 'search': search})


@login_required
def parent_create_view(request):
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
        whatsapp = request.POST.get('whatsapp', '')
        email = request.POST.get('email', '')
        profession = request.POST.get('profession', '')
        adresse = request.POST.get('adresse', '')
        est_principal = request.POST.get('est_contact_principal') == 'on'
        
        parent = ParentTuteur.objects.create(
            eleve=eleve if eleve else Eleve.objects.get(pk=request.POST.get('eleve')),
            nom=nom, prenom=prenom, lien_parente=lien, telephone=telephone,
            whatsapp=whatsapp, email=email, profession=profession, adresse=adresse,
            est_contact_principal=est_principal
        )
        log_audit(request.user, 'create', 'ParentTuteur', parent, f'Ajout parent: {parent}', request)
        messages.success(request, 'Parent/Tuteur ajouté avec succès.')
        return redirect('parent_list')
    
    eleves = Eleve.objects.filter(statut='actif').order_by('nom', 'prenom')
    return render(request, 'scolarite/parent_form.html', {'eleve': eleve, 'eleves': eleves})


# ==================== Dossiers Médicaux ====================
@login_required
def dossiers_medicaux_view(request):
    if not request.user.has_module_permission('dossiers_medicaux', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les dossiers médicaux.")
        return redirect('dashboard')
    
    eleves_avec_dossier = Eleve.objects.filter(dossier_medical__isnull=False).distinct()
    eleves_sans_dossier = Eleve.objects.filter(dossier_medical__isnull=True, statut='actif')
    
    search = request.GET.get('search', '')
    if search:
        eleves_avec_dossier = eleves_avec_dossier.filter(nom__icontains=search)
            
    return render(request, 'scolarite/dossiers_medical.html', {
        'eleves_avec_dossier': eleves_avec_dossier,
        'eleves_sans_dossier': eleves_sans_dossier,
        'search': search
    })


@login_required
def dossiers_medicaux_view(request):
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
        dossier.allergies_medicamenteuses = request.POST.get('allergies_medicamenteuses', '')
        dossier.maladies_chroniques = request.POST.get('maladies_chroniques', '')
        dossier.contacts_urgence_nom = request.POST.get('contacts_urgence_nom', '')
        dossier.contacts_urgence_tel = request.POST.get('contacts_urgence_tel', '')
        dossier.contacts_urgence_lien = request.POST.get('contacts_urgence_lien', '')
        dossier.medecin_traitant = request.POST.get('medecin_traitant', '')
        dossier.tel_medecin = request.POST.get('tel_medecin', '')
        dossier.observations = request.POST.get('observations', '')
        dossier.save()
        
        log_audit(request.user, 'update', 'DossierMedical', dossier, f'Mise à jour dossier médical: {eleve}', request)
        messages.success(request, 'Dossier médical mis à jour.')
        return redirect('dossiers_medical')
    
    return render(request, 'scolarite/dossier_medical_form.html', {'eleve': eleve, 'dossier': dossier})


# ==================== Documents Élève ====================
@login_required
def documents_eleve_view(request):
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
def documents_eleve_view(request):
    if not request.user.has_module_permission('documents_eleve', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'uploader des documents.")
        return redirect('scolarite:documents_eleve')
    
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    
    if request.method == 'POST':
        type_doc = request.POST.get('type_document')
        fichier = request.FILES.get('fichier')
        description = request.POST.get('description', '')
        
        if fichier:
            doc = DocumentEleve.objects.create(
                eleve=eleve,
                type_document=type_doc,
                fichier=fichier,
                description=description
            )
            log_audit(request.user, 'create', 'DocumentEleve', doc, f'Ajout document: {eleve}', request)
            messages.success(request, 'Document ajouté avec succès.')
        return redirect('scolarite:eleve_detail', pk=eleve_id)
    
    return render(request, 'scolarite/document_upload.html', {'eleve': eleve})


@login_required
def documents_eleve_view(request):
    if not request.user.has_module_permission('documents_eleve', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer des documents.")
        return redirect('scolarite:documents_eleve')
    
    doc = get_object_or_404(DocumentEleve, pk=pk)
    eleve_pk = doc.eleve.pk
    eleve_nom = doc.eleve.nom_complet
    
    if request.user.is_superadmin() or request.user.is_direction():
        doc.fichier.delete()
        doc.delete()
        log_audit(request.user, 'delete', 'DocumentEleve', None, f'Suppression document: {eleve_nom}', request)
        messages.success(request, 'Document supprimé avec succès.')
    else:
        details = f"Demande de suppression du document: {doc.get_type_document_display()} de l'élève {eleve_nom}"
        
        demande = DemandeApprobation.objects.create(
            demandeur=request.user,
            type_action=DemandeApprobation.TypeAction.SUPPRESSION,
            type_objet=DemandeApprobation.TypeObjet.DOCUMENT,
            objet_id=doc.pk,
            objet_repr=str(doc),
            details=details,
            details_apos=details
        )
        
        from accounts.models import Notification, User
        approbateurs = User.objects.filter(role__in=[User.Role.SUPERADMIN, User.Role.DIRECTION], is_active=True)
        for approbateur in approbateurs:
            Notification.creer_notification(
                destinataire=approbateur,
                type_notification=Notification.TypeNotification.AUTRE,
                titre="Demande d'approbation - Suppression document",
                message=f"{request.user.get_full_name() or request.user.username} demande la suppression d'un document de l'élève: {eleve_nom}",
                expediteur=request.user,
                lien='/authentification/demandes/'
            )
        
        messages.success(request, 'Votre demande de suppression a été soumise pour approbation.')
    
        return redirect('scolarite:eleve_detail', pk=eleve_pk)


# ==================== Discipline ====================
@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à ce module.")
        return redirect('dashboard')
    
    disciplines = DisciplineEleve.objects.select_related('eleve', 'enregistre_par', 'traite_par').order_by('-date_incident')
    
    type_filter = request.GET.get('type', '')
    statut_filter = request.GET.get('statut', '')
    search = request.GET.get('search', '')
    classe_filter = request.GET.get('classe', '')
    service_filter = request.GET.get('service', '')
    gravity_filter = request.GET.get('gravity', '')
    
    if type_filter:
        disciplines = disciplines.filter(type=type_filter)
            if statut_filter:
        disciplines = disciplines.filter(statut_traitement=statut_filter)
            if search:
        if search.isdigit():
            disciplines = disciplines.filter(eleve_id=int(search))
        else:
            disciplines = disciplines.filter(eleve__nom__icontains=search) | disciplines.filter(eleve__prenom__icontains=search)
    if classe_filter:
        disciplines = disciplines.filter(eleve__inscriptions__classe_id=classe_filter)
            
    periode_filter = request.GET.get('periode', '')
    if periode_filter:
        disciplines = disciplines.filter(periode=periode_filter)
            
    if service_filter:
        disciplines = disciplines.filter(service_traitant=service_filter)
            
    if gravity_filter:
        if gravity_filter == 'legere':
            disciplines = disciplines.filter(points__lte=-1, points__gte=-3)
        elif gravity_filter == 'moyenne':
            disciplines = disciplines.filter(points__lte=-4, points__gte=-7)
        elif gravity_filter == 'grave':
            disciplines = disciplines.filter(points__lte=-8)
            
    paginator = Paginator(disciplines, 30)
    page = request.GET.get('page')
    disciplines_page = paginator.get_page(page)
    
    from decimal import Decimal
    for d in disciplines_page:
        if d.inscription and d.statut_traitement == 'traite':
            # Récupérer la note de base configurée pour ce niveau
            note_base = Decimal('20')
            config = ConduiteConfig.objects.filter(
                annee_scolaire=d.inscription.annee_scolaire,
                niveau=d.inscription.classe.niveau
            ).first()
            if config:
                note_base = config.note_base
            
            # Calculer les déductions/recompenses depuis les disciplines traitées
            total_deductions = Decimal('0')
            total_recompenses = Decimal('0')
            disciplines_inscription = DisciplineEleve.objects.filter(
                inscription=d.inscription,
                statut_traitement='traite'
            )
            for disc in disciplines_inscription:
                if disc.points < 0:
                    total_deductions += Decimal(str(abs(disc.points)))
                elif disc.points > 0:
                    total_recompenses += Decimal(str(disc.points))
            
            # Calculer la note finale
            note_finale = note_base - total_deductions + total_recompenses
            if note_finale > 20:
                note_finale = Decimal('20')
            if note_finale < Decimal('-20'):
                note_finale = Decimal('-20')
            
            d.conduite_restante = float(note_finale)
        else:
            d.conduite_restante = None
    
    from enseignement.models import Classe
    classes = Classe.objects.all().order_by('niveau', 'nom')
    
    return render(request, 'scolarite/discipline_list.html', {
        'disciplines': disciplines_page,
        'type_filter': type_filter,
        'statut_filter': statut_filter,
        'periode_filter': periode_filter,
        'service_filter': service_filter,
        'gravity_filter': gravity_filter,
        'search': search,
        'classe_filter': classe_filter,
        'classes': classes,
        'all_eleves': Eleve.objects.filter(statut='actif').order_by('nom', 'prenom')[:100],
        'can_add': request.user.is_professeur() or request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin(),
        'can_treat': request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin(),
        'can_edit': request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin(),
        'can_delete': request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin(),
    })


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation d'enregistrer une discipline.")
        return redirect('dashboard')
    
    eleves = Eleve.objects.filter(statut='actif').order_by('nom', 'prenom')
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve')
        type_discipline = request.POST.get('type')
        type_detail = request.POST.get('type_detail')
        points = int(request.POST.get('points', 0))
        description = request.POST.get('description')
        date_incident = request.POST.get('date_incident')
        est_signale = request.POST.get('est_signale') == 'on'
        
        inscription = None
        if annee:
            inscription = Inscription.objects.filter(eleve_id=eleve_id, annee_scolaire=annee).first()
        
        is_hierarchie = request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin()
        
        # Déterminer la période en fonction des clotures
        # Si P1 non cloturée -> période = 1
        # Si P1 cloturée et P2 non cloturée -> période = 2
        # Si P2 cloturée et P3 non cloturée -> période = 3
        periode = 1  # Par défaut, tant qu'aucune clôture n'est faite
        if inscription and inscription.classe:
            classe = inscription.classe
            
            # Vérifier si P1 est cloturée
            p1_cloture = PeriodeCloture.objects.filter(classe=classe, periode=1).exists()
            if p1_cloture:
                # Vérifier si P2 est cloturée
                p2_cloture = PeriodeCloture.objects.filter(classe=classe, periode=2).exists()
                if p2_cloture:
                    # Vérifier si P3 est cloturée (pour trimestriel)
                    if annee and annee.type_cycle_actif == 'trimestriel':
                        p3_cloture = PeriodeCloture.objects.filter(classe=classe, periode=3).exists()
                        if p3_cloture:
                            periode = 3  # Toutes les périodes sont cloturées
                        else:
                            periode = 3
                    else:
                        periode = 2  # Semestriel, seulement 2 périodes
                else:
                    periode = 2
            else:
                periode = 1  # P1 non cloturée, tout va dans P1
        
        service_map = {
            'surveillance': 'Surveillance et Contrôle',
            'direction': 'Direction Générale',
            'admin': 'Administrateur'
        }
        
        discipline = DisciplineEleve.objects.create(
            eleve_id=eleve_id,
            inscription=inscription,
            type=type_discipline,
            type_detail=type_detail,
            description=description,
            date_incident=date_incident,
            periode=periode,
            enregistre_par=request.user,
            points=points,
            est_signale=est_signale,
            statut_traitement='traite' if is_hierarchie else 'en_attente',
            traite_par=request.user if is_hierarchie else None,
            service_traitant=service_map.get(request.user.role, '') if is_hierarchie else '',
            date_traitement=timezone.now() if is_hierarchie else None
        )
        
        if is_hierarchie and inscription and points != 0:
            # Récupérer la note de base configurée pour ce niveau
            from decimal import Decimal
            note_base = Decimal('20')
            if inscription.classe:
                config = ConduiteConfig.objects.filter(
                    annee_scolaire=inscription.annee_scolaire,
                    niveau=inscription.classe.niveau
                ).first()
                if config:
                    note_base = config.note_base
            
            conduite, created = ConduiteEleve.objects.get_or_create(
                inscription=inscription,
                defaults={'note_base': note_base, 'total_deductions': Decimal('0'), 'total_recompenses': Decimal('0'), 'note_finale': note_base}
            )
            
            # Si la conduite existait déjà, mettre à jour la note_base avec la config
            if not created and inscription.classe:
                config = ConduiteConfig.objects.filter(
                    annee_scolaire=inscription.annee_scolaire,
                    niveau=inscription.classe.niveau
                ).first()
                if config:
                    conduite.note_base = config.note_base
                    conduite.save()
            
            if points < 0:
                conduite.ajouter_deduction(abs(points), discipline)
            elif points > 0:
                conduite.ajouter_recompense(points, discipline)
        
        if not is_hierarchie:
            services = User.objects.filter(role__in=['surveillance', 'direction', 'superadmin'], is_active=True)
            for user in services:
                titre = f"Nouvelle discipline en attente de traitement"
                message = f"L'élève {discipline.eleve.nom_complet} a été signalé(e) par {request.user.get_full_name() or request.user.username}. Type: {discipline.get_type_display()} - {discipline.get_type_detail_display()}"
                Notification.creer_notification(
                    destinataire=user,
                    type_notification=Notification.TypeNotification.AUTRE,
                    titre=titre,
                    message=message,
                    expediteur=request.user,
                    lien=f'/scolarite/discipline/{discipline.pk}/'
                )
        
        log_audit(request.user, 'create', 'DisciplineEleve', discipline, f'Inscription discipline: {discipline.eleve}', request)
        messages.success(request, 'Discipline enregistrée.')
        return redirect('scolarite:discipline_list')
    
    return render(request, 'scolarite/discipline_form.html', {
        'eleves': eleves,
        'can_add': request.user.is_professeur() or request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin()
    })


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de traiter une discipline.")
        return redirect('dashboard')
    
    discipline = get_object_or_404(DisciplineEleve, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'traiter':
            new_points = int(request.POST.get('points', discipline.points))
            old_points = discipline.points
            
            service_map = {
                'surveillance': 'Surveillance et Contrôle',
                'direction': 'Direction Générale',
                'superadmin': 'Administrateur'
            }
            
            discipline.statut_traitement = 'traite'
            discipline.points = new_points
            discipline.traite_par = request.user
            discipline.service_traitant = service_map.get(request.user.role, request.user.get_role_display())
            discipline.date_traitement = timezone.now()
            discipline.save()
            
            if discipline.inscription and new_points != 0:
                recalculer_conduite(discipline.inscription)
            
            profs = User.objects.filter(role='professeur', is_active=True)
            for prof in profs:
                titre = f"Discipline traitée pour {discipline.eleve.nom_complet}"
                message = f"La discipline de type {discipline.get_type_display()} - {discipline.get_type_detail_display()} a été traitée par {discipline.service_traitant}"
                Notification.creer_notification(
                    destinataire=prof,
                    type_notification=Notification.TypeNotification.AUTRE,
                    titre=titre,
                    message=message,
                    lien=f'/scolarite/discipline/{discipline.pk}/'
                )
            
            messages.success(request, 'Discipline traitée avec succès.')
        
        elif action == 'rejeter':
            discipline.statut_traitement = 'rejete'
            discipline.save()
            messages.warning(request, 'Discipline rejetée.')
        
        return redirect('scolarite:discipline_list')
    
        return redirect('scolarite:discipline_detail', pk=pk)


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette configuration.")
        return redirect('dashboard')
    
    from finances.models import AnneeScolaire
    
    annee_scolaire = AnneeScolaire.objects.filter(est_active=True).first()
    configs = ConduiteConfig.objects.all()
    
    if annee_scolaire:
        configs = configs.filter(annee_scolaire=annee_scolaire)
            
    from enseignement.models import Classe
    niveaux = Classe.Niveau.choices
    
    return render(request, 'scolarite/conduite_config_list.html', {
        'configs': configs,
        'annee_scolaire': annee_scolaire,
        'niveaux': niveaux
    })


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette configuration.")
        return redirect('dashboard')
    
    from finances.models import AnneeScolaire
    from enseignement.models import Classe
    
    annee_scolaire = AnneeScolaire.objects.filter(est_active=True).first()
    
    if request.method == 'POST':
        niveau = request.POST.get('niveau')
        note_base = request.POST.get('note_base')
        
        if annee_scolaire and niveau and note_base:
            ConduiteConfig.objects.update_or_create(
                annee_scolaire=annee_scolaire,
                niveau=niveau,
                defaults={
                    'note_base': note_base,
                    'cree_par': request.user
                }
            )
            messages.success(request, f'Note de conduite configurée pour {niveau}')
        return redirect('scolarite:conduite_config_list')
    
    config = None
    if niveau and annee_scolaire:
        config = ConduiteConfig.objects.filter(annee_scolaire=annee_scolaire, niveau=niveau).first()
            
    niveaux = Classe.Niveau.choices
    
    return render(request, 'scolarite/conduite_config_form.html', {
        'config': config,
        'annee_scolaire': annee_scolaire,
        'niveaux': niveaux,
        'selected_niveau': niveau
    })


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir cette discipline.")
        return redirect('dashboard')
    
    discipline = get_object_or_404(DisciplineEleve.objects.select_related('eleve', 'enregistre_par', 'traite_par'), pk=pk)
    
    conduite = None
    if discipline.inscription:
        conduite = ConduiteEleve.objects.filter(inscription=discipline.inscription).first()
            
    return render(request, 'scolarite/discipline_detail.html', {
        'discipline': discipline,
        'conduite': conduite,
        'can_treat': request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin(),
        'can_edit': request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin(),
    })


def recalculer_conduite(inscription):
    if not inscription:
        return
            
    from decimal import Decimal
    # Récupérer la note de base configurée pour ce niveau
    note_base = Decimal('20')
    if inscription.classe:
        config = ConduiteConfig.objects.filter(
            annee_scolaire=inscription.annee_scolaire,
            niveau=inscription.classe.niveau
        ).first()
        if config:
            note_base = config.note_base
            
    conduite, created = ConduiteEleve.objects.get_or_create(
        inscription=inscription,
        defaults={'note_base': note_base, 'total_deductions': Decimal('0'), 'total_recompenses': Decimal('0'), 'note_finale': note_base}
    )
    
    # Toujours mettre à jour la note_base avec la config (au cas où elle aurait changé)
    conduite.note_base = note_base
    
    disciplines = DisciplineEleve.objects.filter(
        inscription=inscription,
        statut_traitement='traite'
    ).order_by('date_incident')
    
    total_deductions = 0
    total_recompenses = 0
    
    for d in disciplines:
        if d.points < 0:
            total_deductions += abs(d.points)
        elif d.points > 0:
            total_recompenses += d.points
            
    conduite.total_deductions = total_deductions
    conduite.total_recompenses = total_recompenses
    conduite.calculer_note()
    conduite.save()


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette discipline.")
        return redirect('dashboard')
    
    discipline = get_object_or_404(DisciplineEleve, pk=pk)
    eleves = Eleve.objects.filter(statut='actif').order_by('nom', 'prenom')
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    is_hierarchie = request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin()
    is_prof = request.user.is_professeur()
    
    if request.method == 'POST':
        old_points = discipline.points
        old_inscription = discipline.inscription
        
        discipline.eleve_id = request.POST.get('eleve')
        discipline.type = request.POST.get('type')
        discipline.type_detail = request.POST.get('type_detail')
        discipline.points = int(request.POST.get('points', 0))
        discipline.description = request.POST.get('description')
        discipline.date_incident = request.POST.get('date_incident')
        
        new_inscription = Inscription.objects.filter(eleve_id=discipline.eleve_id, annee_scolaire=annee).first()
        discipline.inscription = new_inscription
        
        if is_prof and not is_hierarchie:
            discipline.statut_traitement = 'en_attente'
            discipline.traite_par = None
            discipline.service_traitant = ''
            discipline.date_traitement = None
            
            services = User.objects.filter(role__in=['surveillance', 'direction', 'superadmin'], is_active=True)
            for user in services:
                Notification.creer_notification(
                    destinataire=user,
                    type_notification=Notification.TypeNotification.AUTRE,
                    titre=f"Demande de modification - {discipline.eleve.nom_complet}",
                    message=f"{request.user.get_full_name()} a demandé la modification de la discipline.",
                    expediteur=request.user,
                    lien=f'/scolarite/discipline/{discipline.pk}/'
                )
            messages.info(request, 'Votre demande de modification a été soumise pour approbation.')
        else:
            discipline.statut_traitement = 'traite'
            discipline.traite_par = request.user
            discipline.service_traitant = request.user.get_role_display()
            discipline.date_traitement = timezone.now()
            messages.success(request, 'Discipline modifiée avec succès.')
        
        discipline.save()
        
        if old_inscription and old_inscription != new_inscription:
            recalculer_conduite(old_inscription)
        if new_inscription:
            recalculer_conduite(new_inscription)
        
        log_audit(request.user, 'update', 'DisciplineEleve', discipline, f'Modification discipline: {discipline.eleve}', request)
        return redirect('scolarite:discipline_list')
    
    return render(request, 'scolarite/discipline_form.html', {
        'eleves': eleves,
        'discipline': discipline,
        'can_add': True
    })


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette discipline.")
        return redirect('dashboard')
    
    discipline = get_object_or_404(DisciplineEleve, pk=pk)
    
    is_hierarchie = request.user.is_surveillance() or request.user.is_direction() or request.user.is_superadmin()
    is_prof = request.user.is_professeur()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        inscription = discipline.inscription
        
        if action == 'confirmer':
            discipline.delete()
            if inscription:
                recalculer_conduite(inscription)
            messages.success(request, 'Discipline supprimée avec succès.')
        elif action == 'demander':
            services = User.objects.filter(role__in=['surveillance', 'direction', 'superadmin'], is_active=True)
            for user in services:
                Notification.creer_notification(
                    destinataire=user,
                    type_notification=Notification.TypeNotification.AUTRE,
                    titre=f"Demande de suppression - {discipline.eleve.nom_complet}",
                    message=f"{request.user.get_full_name()} a demandé la suppression de la discipline.",
                    expediteur=request.user,
                    lien=f'/scolarite/discipline/{discipline.pk}/'
                )
            messages.info(request, 'Votre demande de suppression a été soumise pour approbation.')
        
        return redirect('scolarite:discipline_list')
    
    return render(request, 'scolarite/discipline_delete.html', {
        'discipline': discipline
    })


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les statistiques de discipline.")
        return redirect('dashboard')
    
    from django.db.models import Count, Sum, Q
    from django.db.models.functions import TruncMonth
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    disciplines = DisciplineEleve.objects.all()
    if annee:
        disciplines = disciplines.filter(inscription__annee_scolaire=annee)
            
    # Stats globales
    total_sanctions = disciplines.filter(type='sanction').count()
    total_recompenses = disciplines.filter(type='recompense').count()
    total_en_attente = disciplines.filter(statut_traitement='en_attente').count()
    
    # Par période
    periode_stats = []
    for p in [1, 2, 3]:
        p_count = disciplines.filter(periode=p, type='sanction').count()
        periode_stats.append({'periode': p, 'count': p_count})
    
    # Par mois (6 derniers mois)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_stats = disciplines.filter(
        date_incident__gte=six_months_ago.date()
    ).annotate(
        month=TruncMonth('date_incident')
    ).values('month').annotate(
        count=Count('id'),
        sanctions=Count('id', filter=Q(type='sanction')),
        recompenses=Count('id', filter=Q(type='recompense'))
    ).order_by('month')
    
    # Par classe
    class_stats = disciplines.filter(
        inscription__isnull=False,
        type='sanction'
    ).values(
        'inscription__classe__nom'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top élèves avec sanctions
    top_eleves = disciplines.filter(
        type='sanction',
        inscription__isnull=False
    ).values(
        'eleve__nom', 'eleve__prenom', 'eleve__id'
    ).annotate(
        total_points=Sum('points'),
        nb_sanctions=Count('id')
    ).order_by('total_points')[:10]
    
    # Par service traitant
    service_stats = disciplines.filter(
        service_traitant__isnull=False
    ).values('service_traitant').annotate(count=Count('id'))
    
    # Calculer la conduite par niveau
    niveau_conduite = []
    from enseignement.models import Classe
    for niveau_choice, niveau_label in Classe.Niveau.choices[:13]:
        config = ConduiteConfig.objects.filter(niveau=niveau_choice).first()
        if config:
            niveau_conduite.append({
                'niveau': niveau_label,
                'note_base': config.note_base,
                'note_moyenne': float(config.note_base)  # À calculer selon les disciplines
            })
    
    return render(request, 'scolarite/discipline_statistics.html', {
        'total_sanctions': total_sanctions,
        'total_recompenses': total_recompenses,
        'total_en_attente': total_en_attente,
        'periode_stats': periode_stats,
        'monthly_stats': list(monthly_stats),
        'class_stats': list(class_stats),
        'top_eleves': list(top_eleves),
        'service_stats': list(service_stats),
        'niveau_conduite': niveau_conduite,
        'annee_scolaire': annee,
    })


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir l'historique de discipline.")
        return redirect('dashboard')
    
    from decimal import Decimal
    
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    disciplines = DisciplineEleve.objects.filter(eleve=eleve).order_by('-date_incident')
    
    if annee:
        inscriptions = Inscription.objects.filter(eleve=eleve, annee_scolaire=annee)
            else:
        inscriptions = eleve.inscriptions.all()
    
    # Calculer la conduite par période
    conduite_stats = []
    for periode in [1, 2, 3]:
        periode_disciplines = disciplines.filter(periode=periode, statut_traitement='traite', type='sanction')
        total_deductions = sum(abs(d.points) for d in periode_disciplines)
        
        note_base = Decimal('20')
        if inscriptions.exists():
            inscription = inscriptions.first()
            config = ConduiteConfig.objects.filter(
                annee_scolaire=inscription.annee_scolaire,
                niveau=inscription.classe.niveau
            ).first()
            if config:
                note_base = config.note_base
        
        note_finale = float(note_base - Decimal(str(total_deductions)))
        if note_finale < 0:
            note_finale = 0
        
        conduite_stats.append({
            'periode': periode,
            'note_base': float(note_base),
            'deductions': total_deductions,
            'note_finale': note_finale,
            'nb_sanctions': periode_disciplines.count()
        })
    
    return render(request, 'scolarite/discipline_history.html', {
        'eleve': eleve,
        'disciplines': disciplines,
        'conduite_stats': conduite_stats,
        'annee_scolaire': annee,
    })


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation d'exporter les données de discipline.")
        return redirect('dashboard')
    
    from django.http import HttpResponse
    import csv
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    disciplines = DisciplineEleve.objects.all()
    if annee:
        disciplines = disciplines.filter(inscription__annee_scolaire=annee)
            
    # Filtres
    type_filter = request.GET.get('type', '')
    statut_filter = request.GET.get('statut', '')
    periode_filter = request.GET.get('periode', '')
    classe_filter = request.GET.get('classe', '')
    service_filter = request.GET.get('service', '')
    
    if type_filter:
        disciplines = disciplines.filter(type=type_filter)
            if statut_filter:
        disciplines = disciplines.filter(statut_traitement=statut_filter)
            if periode_filter:
        disciplines = disciplines.filter(periode=periode_filter)
            if classe_filter:
        disciplines = disciplines.filter(eleve__inscriptions__classe_id=classe_filter)
            if service_filter:
        disciplines = disciplines.filter(service_traitant=service_filter)
            
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="discipline_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Trimestre', 'Élève', 'Classe', 'Type', 'Détails', 'Points', 'Statut', 'Service', 'Traité par'])
    
    for d in disciplines:
        writer.writerow([
            d.date_incident.strftime('%d/%m/%Y'),
            d.periode or '',
            d.eleve.nom_complet,
            d.inscription.classe.nom if d.inscription else '',
            d.get_type_display(),
            d.get_type_detail_display(),
            d.points,
            d.get_statut_traitement_display(),
            d.service_traitant or '',
            d.traite_par.get_full_name() if d.traite_par else '',
        ])
    
    return response


@login_required
def discipline_list(request):
    if not request.user.has_module_permission('discipline', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation de traiter les disciplines.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        discipline_ids = request.POST.getlist('discipline_ids')
        action = request.POST.get('action', 'traite')
        
        if discipline_ids:
            if action == 'traite':
                DisciplineEleve.objects.filter(pk__in=discipline_ids).update(
                    statut_traitement='traite',
                    traite_par=request.user,
                    service_traitant=request.user.get_role_display(),
                    date_traitement=timezone.now()
                )
                messages.success(request, f'{len(discipline_ids)} discipline(s) traitée(s) avec succès.')
            elif action == 'delete':
                count = DisciplineEleve.objects.filter(pk__in=discipline_ids, statut_traitement='traite').delete()[0]
                messages.success(request, f'{count} discipline(s) supprimée(s).')
    
        return redirect('scolarite:discipline_list')


@login_required
def view_func(request):
    from enseignement.models import Classe
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    # Only principal, direction or admin can access this page
    if hasattr(request.user, 'professeur') and request.user.professeur:
        # Must be principal of at least one class
        classes = Classe.objects.filter(professeur_principal=request.user.professeur, annee_scolaire=annee)
        if not classes.exists() and not request.user.is_direction() and not request.user.is_superadmin():
        messages.error(request, "Vous n'êtes pas professeur principal d'une classe.")
        return redirect('dashboard')
    elif not request.user.is_direction() and not request.user.is_superadmin():
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('dashboard')
    else:
        classes = Classe.objects.filter(annee_scolaire=annee) if annee else Classe.objects.none()
    
    classe_data = []
    for classe in classes:
        clotures = {}
        for p in [1, 2, 3]:
            cloture = PeriodeCloture.objects.filter(classe=classe, periode=p).first()
            clotures[p] = cloture
        
        # Déterminer quelle période est la prochaine à clôturer
        prochaine_periode = 1
        if clotures.get(1):
            prochaine_periode = 2 if clotures.get(2) is None or not clotures.get(2) else (3 if clotures.get(3) is None else 3)
            if annee and annee.type_cycle_actif == 'semestriel':
                prochaine_periode = 2
        
        classe_data.append({
            'classe': classe,
            'clotures': clotures,
            'prochaine_periode': prochaine_periode,
            'type_cycle': annee.type_cycle_actif if annee else 'trimestriel'
        })
    
    return render(request, 'scolarite/periode_cloture_list.html', {
        'classe_data': classe_data,
        'annee_scolaire': annee,
    })


@login_required
def view_func(request):
    from enseignement.models import Classe, Enseignement
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    classe = get_object_or_404(Classe, pk=classe_id)
    annee = classe.annee_scolaire
    
    # Check if user is the principal of this class or is direction/admin
    if hasattr(request.user, 'professeur') and request.user.professeur:
        if classe.professeur_principal != request.user.professeur and not request.user.is_superadmin():
        messages.error(request, "Seul le professeur principal peut clôturer une période.")
        return redirect('scolarite:periode_cloture_list')
    else:
        if not request.user.is_superadmin() and not request.user.is_direction():
        messages.error(request, "Vous n'êtes pas autorisé à clôturer cette période.")
        return redirect('scolarite:periode_cloture_list')
    
    # Check if all professors have closed their notes for this period before allowing closure
    def can_close_period(periode):
        enseignements = Enseignement.objects.filter(classe=classe)
        clotures_count = NotePeriodeCloture.objects.filter(classe=classe, periode=periode).count()
        return clotures_count >= enseignements.count()
    
    if request.method == 'POST':
        periode = int(request.POST.get('periode'))
        observations = request.POST.get('observations', '')
        
        # Verify all profs have closed their notes
        if not can_close_period(periode):
        messages.error(request, "Impossible de clôturer la période. Tous les professors doivent d'abord clôturer leurs notes.")
        return redirect('scolarite:periode_cloture_edit', classe_id)
        
        # Create or update cloture
        cloture, created = PeriodeCloture.objects.update_or_create(
            classe=classe,
            periode=periode,
            defaults={
                'cloture_par': request.user,
                'observations': observations
            }
        )
        
        messages.success(request, f'Période {periode} cloturée avec succès pour la classe {classe.nom}')
        return redirect('scolarite:periode_cloture_list')
    
    # Get current clotures
    clotures = {}
    for p in [1, 2, 3]:
        clotures[p] = PeriodeCloture.objects.filter(classe=classe, periode=p).first()
            
    # Determine which periods are still open
    periods_open = []
    if not clotures.get(1):
        periods_open.append(1)
            elif not clotures.get(2):
        periods_open.append(2)
            elif not clotures.get(3):
        periods_open.append(3)
            
    return render(request, 'scolarite/periode_cloture_form.html', {
        'classe': classe,
        'clotures': clotures,
        'periods_open': periods_open,
        'type_cycle': annee.type_cycle_actif if annee else 'trimestriel'
        })


@login_required
def periode_cloture_list(request):
    from enseignement.models import Classe
    
    classe = get_object_or_404(Classe, pk=classe_id)
    
    # Only principal, direction or admin can delete a cloture
    if hasattr(request.user, 'professeur') and request.user.professeur:
        if classe.professeur_principal != request.user.professeur and not request.user.is_superadmin():
        messages.error(request, "Seul le professeur principal peut supprimer une clôture.")
        return redirect('scolarite:periode_cloture_list')
    else:
        if not request.user.is_superadmin() and not request.user.is_direction():
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette clôture.")
        return redirect('scolarite:periode_cloture_list')
    
    cloture = PeriodeCloture.objects.filter(classe=classe, periode=periode).first()
    if cloture:
        cloture.delete()
        messages.success(request, f'La clôture de la période {periode} a été supprimée pour la classe {classe}.')
    else:
        messages.error(request, 'Clôture non trouvée.')
    
        return redirect('scolarite:periode_cloture_list')


@login_required
def view_func(request):
    from enseignement.models import Classe, Enseignement
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    # Only professors can close their notes
    if not hasattr(request.user, 'professeur') or not request.user.professeur:
        if not request.user.is_direction() and not request.user.is_superadmin():
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('dashboard')
    
    # Get classes where the user is a professor (either teaching or principal)
    if hasattr(request.user, 'professeur') and request.user.professeur:
        prof = request.user.professeur
        
        # Classes where user teaches
        classes_teaches = Enseignement.objects.filter(
            professeur=prof,
            classe__annee_scolaire=annee
        ).values_list('classe_id', flat=True).distinct()
        
        # Classes where user is principal
        classes_principal = Classe.objects.filter(
            professeur_principal=prof,
            annee_scolaire=annee
        ).values_list('id', flat=True)
        
        # Combine both
        class_ids = list(set(list(classes_teaches) + list(classes_principal)))
        classes = Classe.objects.filter(id__in=class_ids, annee_scolaire=annee)
    elif request.user.is_direction() or request.user.is_superadmin():
        # Direction/admin sees all classes
        classes = Classe.objects.filter(annee_scolaire=annee) if annee else Classe.objects.none()
    else:
        classes = Classe.objects.none()
    
    classe_data = []
    for classe in classes:
        # Get all professors teaching this class
        enseignements = Enseignement.objects.filter(classe=classe)
        profs_data = []
        
        for ens in enseignements:
            prof_clotures = {}
            for p in [1, 2, 3]:
                cloture = NotePeriodeCloture.objects.filter(
                    classe=classe,
                    professeur=ens.professeur,
                    periode=p
                ).first()
                prof_clotures[p] = cloture
            
            # Check if this professor has completed all for current period
            is_complete = True
            for ens_check in enseignements:
                for p_check in [1, 2, 3]:
                    if not NotePeriodeCloture.objects.filter(
                        classe=classe,
                        professeur=ens_check.professeur,
                        periode=p_check
                    ).exists():
                        is_complete = False
                        break
                if not is_complete:
                    break
            
            profs_data.append({
                'professeur': ens.professeur,
                'clotures': prof_clotures,
                'is_complete': is_complete
            })
        
        # Check period cloture status
        periode_cloture = PeriodeCloture.objects.filter(classe=classe).first()
        
        classe_data.append({
            'classe': classe,
            'professeurs': profs_data,
            'nombre_profs': enseignements.count(),
            'periode_cloture': periode_cloture,
            'is_principal': classe.professeur_principal == prof if hasattr(request.user, 'professeur') and request.user.professeur else False
        })
    
    return render(request, 'scolarite/note_cloture_list.html', {
        'classe_data': classe_data,
        'annee_scolaire': annee,
    })


@login_required
def view_func(request):
    from enseignement.models import Classe, Enseignement, Matiere
    from enseignement.models import Evaluation
    
    classe = get_object_or_404(Classe, pk=classe_id)
    annee = classe.annee_scolaire
    
    prof = None
    if hasattr(request.user, 'professeur'):
        prof = request.user.professeur
            
    # Check if user is either teaching this class or is principal
    is_authorized = False
    if prof:
        is_teaching = Enseignement.objects.filter(classe=classe, professeur=prof).exists()
        is_principal = (classe.professeur_principal == prof)
        is_authorized = is_teaching or is_principal
    
    if not is_authorized and not request.user.is_superadmin():
        messages.error(request, "Vous n'êtes pas autorisé à clôturer les notes de cette classe.")
        return redirect('scolarite:note_cloture_list')
    
    def check_notes_completeness(professeur, periode):
        """Vérifie que toutes les notes d'interrogations et devoirs sont saisies pour ce prof et cette période"""
        from finances.models import AnneeScolaire
        from scolarite.models import Inscription
        
        # Get matiere this professor teaches in this class
        enseignements = Enseignement.objects.filter(classe=classe, professeur=professeur)
        matieres = [ens.matiere for ens in enseignements]
        
        # Get all students in this class for this year
        eleves_ids = Inscription.objects.filter(classe=classe, annee_scolaire=annee).values_list('eleve_id', flat=True)
        total_eleves = len(eleves_ids)
        
        if total_eleves == 0 or not matieres:
            return True, 0, 0  # No students or no subjects, consider complete
        
        # Determine period date range
        if periode == 1:
            start_date = f"{annee.date_debut.year}-01-01"
            end_date = f"{annee.date_debut.year}-04-30"
        elif periode == 2:
            if annee.type_cycle_actif == 'trimestriel':
                start_date = f"{annee.date_debut.year}-05-01"
                end_date = f"{annee.date_debut.year}-08-31"
            else:
                start_date = f"{annee.date_debut.year}-01-01"
                end_date = f"{annee.date_debut.year}-06-30"
        else:  # periode 3
            start_date = f"{annee.date_fin.year}-09-01"
            end_date = f"{annee.date_fin.year}-12-31"
        
        # Count evaluations with notes for this period
        evaluations_with_notes = Evaluation.objects.filter(
            matiere__in=matieres,
            eleve_id__in=eleves_ids,
            date_eval__gte=start_date,
            date_eval__lte=end_date,
            type_eval__in=['interrogation', 'mini_devoir', 'devoir']
        ).values('eleve_id', 'matiere_id').distinct().count()
        
        # Expected: number of students × number of subjects × 2 (interrogation + devoir minimum)
        expected_minimum = total_eleves * len(matieres) * 2
        
        return evaluations_with_notes >= expected_minimum, evaluations_with_notes, expected_minimum
    
    if request.method == 'POST':
        periode = int(request.POST.get('periode'))
        observations = request.POST.get('observations', '')
        
        # Check if all notes are complete before allowing cloture
        if prof:
            is_complete, entered, expected = check_notes_completeness(prof, periode)
            if not is_complete:
        messages.error(request,
                    f"Impossible de clôturer. Vous devez entrer au moins les interrogations et devoirs pour tous les élèves. "
                    f"Notes saisies: {entered}, Minimum attendu: {expected}")
        return redirect('scolarite:note_cloture_edit', classe_id)
        
        # Create or update note cloture
        if prof:
            NotePeriodeCloture.objects.update_or_create(
                classe=classe,
                professeur=prof,
                periode=periode,
                defaults={
                    'cloture_par': request.user,
                    'observations': observations
                }
            )
            messages.success(request, f'Notes du {periode}e trimestre cloturées avec succès.')
        
        return redirect('scolarite:note_cloture_list')
    
    # Get user's clotures for this class
    clotures = {}
    notes_status = {}
    if prof:
        for p in [1, 2, 3]:
            clotures[p] = NotePeriodeCloture.objects.filter(
                classe=classe,
                professeur=prof,
                periode=p
            ).first()
            # Check notes status for each period
            is_complete, entered, expected = check_notes_completeness(prof, p)
            notes_status[p] = {
                'complete': is_complete,
                'entered': entered,
                'expected': expected
            }
    
    # Get all professors and their clotures
    enseignements = Enseignement.objects.filter(classe=classe)
    all_profs_data = []
    for ens in enseignements:
        prof_clotures = {}
        for p in [1, 2, 3]:
            prof_clotures[p] = NotePeriodeCloture.objects.filter(
                classe=classe,
                professeur=ens.professeur,
                periode=p
            ).first()
        all_profs_data.append({
            'professeur': ens.professeur,
            'clotures': prof_clotures
        })
    
    # Check if all profs have clotured for each period
    periods_status = {}
    for p in [1, 2, 3]:
        clotures_count = NotePeriodeCloture.objects.filter(classe=classe, periode=p).count()
        periods_status[p] = {
            'clotured': clotures_count,
            'total': enseignements.count(),
            'complete': clotures_count >= enseignements.count()
        }
    
    # Determine which period can be closed by principal
    can_close_period = None
    for p in [1, 2, 3]:
        if periods_status[p]['complete']:
            if not PeriodeCloture.objects.filter(classe=classe, periode=p).exists():
                can_close_period = p
                break
    
    return render(request, 'scolarite/note_cloture_form.html', {
        'classe': classe,
        'clotures': clotures,
        'notes_status': notes_status,
        'all_profs': all_profs_data,
        'periods_status': periods_status,
        'can_close_period': can_close_period,
        'is_principal': classe.professeur_principal == prof if prof else False,
        'type_cycle': annee.type_cycle_actif if annee else 'trimestriel'
        })
