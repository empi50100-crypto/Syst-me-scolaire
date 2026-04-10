from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from datetime import date

from finances.models import (
    AnneeScolaire, FraisScolaire, Paiement, EcoleCompte, Salaire, Rappel, CycleConfig,
    ChargeFixe, ChargeOperationnelle, Personnel, Facture, LigneFacture, BourseRemise,
    EleveBourse, CategorieDepense, RapportFinancier
)


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
from finances.forms import (
    AnneeScolaireForm, FraisScolaireForm, PaiementForm, EcoleCompteForm, SalaireForm,
    CycleConfigForm, ChargeFixeForm, ChargeOperationnelleForm, PersonnelForm
)
from accounts.models import User


@login_required
def annee_list(request):
    if not request.user.has_module_permission('annee_scolaire', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    annees = AnneeScolaire.objects.all().order_by('-date_debut')
    return render(request, 'finances/annee_list.html', {'annees': annees})


@login_required
def annee_create(request):
    if not request.user.has_module_permission('annee_scolaire', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = AnneeScolaireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Annee creee.')
            return redirect('finances:annee_list')
    else:
        form = AnneeScolaireForm()
    return render(request, 'finances/annee_form.html', {'form': form})


@login_required
def annee_edit(request, pk):
    if not request.user.has_module_permission('annee_scolaire', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    annee = get_object_or_404(AnneeScolaire, pk=pk)
    if request.method == 'POST':
        form = AnneeScolaireForm(request.POST, instance=annee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Annee modifiee.')
            return redirect('finances:annee_list')
    else:
        form = AnneeScolaireForm(instance=annee)
    return render(request, 'finances/annee_form.html', {'form': form})


@login_required
def annee_delete(request, pk):
    if not request.user.has_module_permission('annee_scolaire', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    annee = get_object_or_404(AnneeScolaire, pk=pk)
    if request.method == 'POST':
        annee.delete()
        messages.success(request, 'Annee supprimee.')
    return redirect('finances:annee_list')


@login_required
def annee_activer(request, pk):
    if not request.user.has_module_permission('annee_scolaire', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    AnneeScolaire.objects.filter(est_active=True).update(est_active=False)
    annee = get_object_or_404(AnneeScolaire, pk=pk)
    annee.est_active = True
    annee.save()
    messages.success(request, f'Annee {annee} activee.')
    return redirect('finances:annee_list')


@login_required
def annee_selectionner(request, pk):
    if not request.user.has_module_permission('annee_scolaire', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    return redirect('dashboard')


@login_required
def frais_list(request):
    if not request.user.has_module_permission('frais', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    frais = FraisScolaire.objects.all().order_by('-montant')
    return render(request, 'finances/frais_list.html', {'frais': frais})


@login_required
def frais_create(request):
    if not request.user.has_module_permission('frais', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = FraisScolaireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Frais crees.')
            return redirect('finances:frais_list')
    else:
        form = FraisScolaireForm()
    return render(request, 'finances/frais_form.html', {'form': form})


@login_required
def frais_update(request, pk):
    if not request.user.has_module_permission('frais', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    frais = get_object_or_404(FraisScolaire, pk=pk)
    if request.method == 'POST':
        form = FraisScolaireForm(request.POST, instance=frais)
        if form.is_valid():
            form.save()
            messages.success(request, 'Frais modifies.')
            return redirect('finances:frais_list')
    else:
        form = FraisScolaireForm(instance=frais)
    return render(request, 'finances/frais_form.html', {'form': form})


@login_required
def paiement_list(request):
    if not request.user.has_module_permission('paiements', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    paiements = Paiement.objects.all().order_by('-date_paiement')[:100]
    return render(request, 'finances/paiement_list.html', {'paiements': paiements})


@login_required
def paiement_create(request, eleve_pk=None):
    if not request.user.has_module_permission('paiements', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paiement enregistre.')
            return redirect('finances:paiement_list')
    else:
        form = PaiementForm()
    return render(request, 'finances/paiement_form.html', {'form': form})


@login_required
def recu_paiement(request, paiement_pk):
    if not request.user.has_module_permission('paiements', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    paiement = get_object_or_404(Paiement, pk=paiement_pk)
    return render(request, 'finances/recu.html', {'paiement': paiement})


@login_required
def etat_compte_eleve(request, eleve_pk):
    if not request.user.has_module_permission('paiements', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    from eleves.models import Eleve, Inscription
    from finances.models import AnneeScolaire
    eleve = get_object_or_404(Eleve, pk=eleve_pk)
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    inscriptions = eleve.inscriptions.all()
    paiements = eleve.paiements.all().order_by('-date_paiement')
    return render(request, 'finances/etat_compte.html', {
        'eleve': eleve,
        'inscriptions': inscriptions,
        'paiements': paiements,
        'annee': annee
    })


@login_required
def historique_paiements_eleve(request, eleve_pk):
    if not request.user.has_module_permission('paiements', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    from eleves.models import Eleve
    eleve = get_object_or_404(Eleve, pk=eleve_pk)
    paiements = eleve.paiements.all().order_by('-date_paiement')
    return render(request, 'finances/historique_paiements.html', {'eleve': eleve, 'paiements': paiements})


@login_required
def gestion_salaires(request):
    if not request.user.has_module_permission('salaires', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    from finances.models import Salaire
    salaries_list = list(Salaire.objects.all())
    
    debug_msg = f"User: {request.user.username} | Salaries from DB: {Salaire.objects.count()} | List: {len(salaries_list)}"
    print(f"DEBUG: {debug_msg}")
    
    return render(request, 'finances/salaire_list.html', {
        'salaires': salaries_list,
        'debug_info': debug_msg
    })


@login_required
def salaire_create(request):
    if not request.user.has_module_permission('salaires', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    source = request.GET.get('source', 'system')
    
    if request.method == 'POST':
        form = SalaireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salaire enregistré.')
            return redirect('finances:gestion_salaires')
    else:
        personnel_id = request.GET.get('personnel')
        source = 'manual'
        form = SalaireForm()
        selected_personnel = None
        
        if personnel_id:
            try:
                selected_personnel = Personnel.objects.get(pk=personnel_id)
                form.initial['personnel'] = selected_personnel
                if selected_personnel.salaire_mensuel:
                    form.initial['salaire_brut'] = selected_personnel.salaire_mensuel
            except Personnel.DoesNotExist:
                pass
        else:
            from datetime import datetime
            form.initial['annee'] = 2026
            form.initial['mois'] = datetime.now().month
            form.initial['retenues'] = 0
            source = request.GET.get('source', 'system')
    
    from accounts.models import User
    system_users = User.objects.filter(
        is_active=True,
        role__in=['professeur', 'secretaire', 'comptable', 'surveillance', 'direction', 'agent_securite', 'chauffeur', 'responsable_stock']
    ).select_related('dossier_personnel')
    
    return render(request, 'finances/salaire_form.html', {
        'form': form,
        'source': source,
        'system_users': system_users,
        'selected_personnel': selected_personnel
    })


@login_required
def operation_caisse(request):
    if not request.user.has_module_permission('caisse', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    operations = EcoleCompte.objects.all().order_by('-date_operation')
    
    total_encaissements = operations.filter(type_operation='encaissement').aggregate(total=Sum('montant'))['total'] or 0
    total_decaissements = operations.filter(type_operation='decaissement').aggregate(total=Sum('montant'))['total'] or 0
    solde = total_encaissements - total_decaissements
    
    categories_existantes = EcoleCompte.objects.values_list('categorie', flat=True).distinct()
    
    return render(request, 'finances/caisse.html', {
        'operations': operations,
        'total_encaissements': total_encaissements,
        'total_decaissements': total_decaissements,
        'solde': solde,
        'categories_existantes': categories_existantes,
    })


@login_required
def charges_list(request):
    if not request.user.has_module_permission('charges', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    fixes = ChargeFixe.objects.all()
    operationnelles = ChargeOperationnelle.objects.all()
    return render(request, 'finances/charges_list.html', {
        'fixes': fixes,
        'operationnelles': operationnelles
    })


@login_required
def personnel_list(request):
    if not request.user.has_module_permission('personnel', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    personnel_list = Personnel.objects.all().order_by('-date_embauche')
    total_salaires_mensuels = sum(p.salaire_mensuel or 0 for p in personnel_list if p.est_actif)
    fonction_filter = request.GET.get('fonction')
    if fonction_filter:
        personnel_list = personnel_list.filter(fonction=fonction_filter)
    return render(request, 'finances/personnel_list.html', {
        'personnel_list': personnel_list,
        'total_salaires_mensuels': total_salaires_mensuels,
        'fonction_filter': fonction_filter
    })


@login_required
def personnel_create(request):
    if not request.user.has_module_permission('personnel', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    from accounts.models import User
    system_users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    if request.method == 'POST':
        form = PersonnelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personnel créé.')
            return redirect('finances:personnel_list')
    else:
        user_id = request.GET.get('user')
        form = PersonnelForm()
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                form.initial['nom'] = user.last_name or user.username
                form.initial['prenom'] = user.first_name or ''
                form.initial['compte_utilisateur'] = user
                if user.telephone:
                    form.initial['telephone'] = user.telephone
                
                role_fonction_map = {
                    'direction': 'direction',
                    'secretaire': 'secretaire',
                    'comptable': 'comptable',
                    'professeur': 'professeur',
                    'surveillance': 'surveillance',
                    'agent_securite': 'agent_securite',
                    'chauffeur': 'chauffeur',
                    'responsable_stock': 'responsable_stock',
                }
                fonction = role_fonction_map.get(user.role)
                if fonction:
                    form.initial['fonction'] = fonction
                if user.date_embauche:
                    form.initial['date_embauche'] = user.date_embauche.strftime('%Y-%m-%d')
                elif user.date_joined:
                    form.initial['date_embauche'] = user.date_joined.strftime('%Y-%m-%d')
            except User.DoesNotExist:
                pass
    
    return render(request, 'finances/personnel_form.html', {
        'form': form,
        'system_users': system_users,
        'action': 'create',
        'selected_user_id': int(user_id) if user_id else None
    })


@login_required
def personnel_edit(request, pk):
    if not request.user.has_module_permission('personnel', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    personnel = get_object_or_404(Personnel, pk=pk)
    if request.method == 'POST':
        form = PersonnelForm(request.POST, instance=personnel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personnel modifie.')
            return redirect('finances:personnel_list')
    else:
        form = PersonnelForm(instance=personnel)
    return render(request, 'finances/personnel_form.html', {'form': form})


@login_required
def personnel_delete(request, pk):
    if not request.user.has_module_permission('personnel', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    personnel = get_object_or_404(Personnel, pk=pk)
    if request.method == 'POST':
        personnel.delete()
        messages.success(request, 'Personnel supprime.')
    return redirect('finances:personnel_list')


@login_required
def charge_fixe_create(request):
    if not request.user.has_module_permission('charges', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = ChargeFixeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Charge creee.')
            return redirect('finances:charges_list')
    else:
        form = ChargeFixeForm()
    return render(request, 'finances/charge_form.html', {'form': form})


@login_required
def charge_fixe_edit(request, pk):
    if not request.user.has_module_permission('charges', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    charge = get_object_or_404(ChargeFixe, pk=pk)
    if request.method == 'POST':
        form = ChargeFixeForm(request.POST, instance=charge)
        if form.is_valid():
            form.save()
            messages.success(request, 'Charge modifiee.')
            return redirect('finances:charges_list')
    else:
        form = ChargeFixeForm(instance=charge)
    return render(request, 'finances/charge_form.html', {'form': form})


@login_required
def charge_fixe_delete(request, pk):
    if not request.user.has_module_permission('charges', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    charge = get_object_or_404(ChargeFixe, pk=pk)
    if request.method == 'POST':
        charge.delete()
        messages.success(request, 'Charge supprimee.')
    return redirect('finances:charges_list')


@login_required
def charge_operationnelle_create(request):
    if not request.user.has_module_permission('charges', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = ChargeOperationnelleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Charge creee.')
            return redirect('finances:charges_list')
    else:
        form = ChargeOperationnelleForm()
    return render(request, 'finances/charge_form.html', {'form': form})


@login_required
def charge_operationnelle_delete(request, pk):
    if not request.user.has_module_permission('charges', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    charge = get_object_or_404(ChargeOperationnelle, pk=pk)
    if request.method == 'POST':
        charge.delete()
        messages.success(request, 'Charge supprimee.')
    return redirect('finances:charges_list')


@login_required
def tableau_bord_financier(request):
    if not request.user.has_module_permission('rapport_financier', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    annee = getattr(request, 'annee_active', None)
    
    if not annee:
        try:
            annee = AnneeScolaire.objects.filter(est_active=True).first()
        except Exception:
            pass
    
    frais_query = FraisScolaire.objects.all()
    paiements_query = Paiement.objects.all()
    salaires_query = Salaire.objects.filter(est_paye=True)
    decaissements_query = EcoleCompte.objects.filter(type_operation='decaissement')
    
    if annee:
        annee_filter = annee.date_fin.year
        paiements_query = paiements_query.filter(frais__annee_scolaire=annee)
        salaires_query = salaires_query.filter(annee=annee_filter)
        decaissements_query = decaissements_query.filter(date_operation__gte=annee.date_debut, date_operation__lte=annee.date_fin)
    
    total_frais = calculer_total_frais_avec_eleves(annee) if annee else 0
    total_paiements = paiements_query.aggregate(total=Sum('montant'))['total'] or 0
    nb_paiements = paiements_query.count()
    
    from datetime import datetime
    mois_actuel = datetime.now().month
    annee_actuelle = datetime.now().year
    encaissements_mois = paiements_query.filter(
        date_paiement__month=mois_actuel,
        date_paiement__year=annee_actuelle
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    reste_a_payer = total_frais - total_paiements
    
    total_salaires = salaires_query.aggregate(total=Sum('salaire_net'))['total'] or 0
    
    total_decaissements_caisse = decaissements_query.aggregate(total=Sum('montant'))['total'] or 0
    total_decaissements = total_salaires + total_decaissements_caisse
    
    solde = total_paiements - total_decaissements
    
    taux_recouvrement = (total_paiements / total_frais * 100) if total_frais > 0 else 0
    
    return render(request, 'finances/tableau_bord.html', {
        'annee': annee,
        'total_frais': total_frais,
        'total_paiements': total_paiements,
        'nb_paiements': nb_paiements,
        'encaissements_mois': encaissements_mois,
        'reste_a_payer': reste_a_payer,
        'total_salaires': total_salaires,
        'total_decaissements': total_decaissements,
        'solde': solde,
        'taux_recouvrement': taux_recouvrement,
    })


@login_required
def liste_rappels(request):
    if not request.user.has_module_permission('rappels', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    rappels = Rappel.objects.all().order_by('-date_emission')[:100]
    return render(request, 'finances/rappels.html', {'rappels': rappels})


@login_required
def generer_rappels(request):
    if not request.user.has_module_permission('rappels', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    messages.success(request, 'Rappels generes.')
    return redirect('finances:liste_rappels')


@login_required
def cycle_list(request):
    if not request.user.has_module_permission('annee_scolaire', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    cycles = CycleConfig.objects.all()
    return render(request, 'finances/cycle_list.html', {'cycles': cycles})


@login_required
def cycle_create(request):
    if not request.user.has_module_permission('annee_scolaire', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = CycleConfigForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cycle cree.')
            return redirect('finances:cycle_list')
    else:
        form = CycleConfigForm()
    return render(request, 'finances/cycle_form.html', {'form': form})


@login_required
def cycle_edit(request, pk):
    if not request.user.has_module_permission('annee_scolaire', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    cycle = get_object_or_404(CycleConfig, pk=pk)
    if request.method == 'POST':
        form = CycleConfigForm(request.POST, instance=cycle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cycle modifie.')
            return redirect('finances:cycle_list')
    else:
        form = CycleConfigForm(instance=cycle)
    return render(request, 'finances/cycle_form.html', {'form': form})


@login_required
def cycle_delete(request, pk):
    if not request.user.has_module_permission('annee_scolaire', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    cycle = get_object_or_404(CycleConfig, pk=pk)
    if request.method == 'POST':
        cycle.delete()
        messages.success(request, 'Cycle supprime.')
    return redirect('finances:cycle_list')


@login_required
def eleves_en_retard(request):
    if not request.user.has_module_permission('eleves_retard', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    from eleves.models import Inscription
    from finances.models import FraisScolaire, Paiement
    from django.db.models import Sum
    
    annee = getattr(request, 'annee_active', None)
    if not annee:
        from finances.models import AnneeScolaire
        annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    eleves_retard = []
    total_frais_global = 0
    
    if annee:
        inscriptions = Inscription.objects.filter(annee_scolaire=annee).select_related('eleve', 'classe')
        
        for inscription in inscriptions:
            eleve = inscription.eleve
            classe = inscription.classe
            niveau = classe.niveau
            
            frais_eleve = FraisScolaire.objects.filter(
                annee_scolaire=annee,
                mode_application='niveau',
                niveau=niveau
            ).first()
            
            total_frais = frais_eleve.montant if frais_eleve else 0
            
            paiements = Paiement.objects.filter(eleve=eleve, frais__annee_scolaire=annee)
            total_paye = paiements.aggregate(total=Sum('montant'))['total'] or 0
            
            total_frais_global += total_frais
            
            if total_paye < total_frais:
                eleves_retard.append({
                    'eleve': eleve,
                    'classe': classe,
                    'niveau': niveau,
                    'total_frais': total_frais,
                    'total_paye': total_paye,
                    'reste': total_frais - total_paye
                })
    
    return render(request, 'finances/eleves_retard.html', {
        'eleves_retard': eleves_retard,
        'total_frais_global': total_frais_global,
        'annee': annee
    })


@login_required
def facture_list(request):
    if not request.user.has_module_permission('factures', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    factures = Facture.objects.all().order_by('-date_facture')[:100]
    return render(request, 'finances/facture_list.html', {'factures': factures})


@login_required
def facture_create(request):
    if not request.user.has_module_permission('factures', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    messages.success(request, 'Facture creee.')
    return redirect('finances:facture_list')


@login_required
def facture_detail(request, pk):
    if not request.user.has_module_permission('factures', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    facture = get_object_or_404(Facture, pk=pk)
    return render(request, 'finances/facture_detail.html', {'facture': facture})


@login_required
def facture_pdf(request, pk):
    if not request.user.has_module_permission('factures', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    return HttpResponse("PDF non implemente")


@login_required
def bourse_list(request):
    if not request.user.has_module_permission('bourses', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    bourses = BourseRemise.objects.all()
    return render(request, 'finances/bourse_list.html', {'bourses': bourses})


@login_required
def bourse_create(request):
    if not request.user.has_module_permission('bourses', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    messages.success(request, 'Bourse creee.')
    return redirect('finances:bourse_list')


@login_required
def categorie_depense(request):
    if not request.user.has_module_permission('charges', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    categories = CategorieDepense.objects.all()
    return render(request, 'finances/categorie_depense.html', {'categories': categories})


@login_required
def rapport_financier(request):
    if not request.user.has_module_permission('rapports', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    return render(request, 'finances/rapport.html')
