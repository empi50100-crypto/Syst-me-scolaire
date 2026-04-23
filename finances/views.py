from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from datetime import date, datetime

from core.models import AnneeScolaire, Cycle
from finances.models import (
    FraisScolaire, Paiement, OperationCaisse, RappelPaiement,
    ChargeFixe, ChargeOperationnelle, Facture, LigneFacture, BourseRemise,
    EleveBourse, CategorieDepense, RapportFinancier
)
from finances.forms import (
    AnneeScolaireForm, FraisScolaireForm, PaiementForm, 
    OperationCaisseForm, CycleForm, ChargeFixeForm, ChargeOperationnelleForm
)
from ressources_humaines.models import MembrePersonnel, Salaire
from authentification.models import Utilisateur


def _calculer_total_frais_avec_eleves(annee):
    """Utility function to calculate total expected fees for an academic year"""
    from scolarite.models import EleveInscription
    from enseignement.models import Classe
    from django.db.models import Q
    
    total_frais = 0
    frais_list = FraisScolaire.objects.filter(
        Q(annee_scolaire=annee) | Q(annee_scolaire__isnull=True)
    )
    
    for frais in frais_list:
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


@login_required
def caisse(request):
    if not request.user.has_module_permission('caisse', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    annee_actuelle = AnneeScolaire.objects.filter(est_actif=True).first()
    operations = OperationCaisse.objects.all().order_by('-date_operation')[:50]
    solde_total = OperationCaisse.objects.aggregate(
        total=Sum('montant')
    )['total'] or 0
    return render(request, 'finances/caisse.html', {
        'operations': operations,
        'solde_total': solde_total,
        'annee_actuelle': annee_actuelle
    })


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
            messages.success(request, 'Année scolaire créée.')
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
            messages.success(request, 'Année scolaire modifiée.')
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
        messages.success(request, 'Année scolaire supprimée.')
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
    messages.success(request, f'Année {annee} activée.')
    return redirect('finances:annee_list')


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
            messages.success(request, 'Frais scolaires créés.')
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
            messages.success(request, 'Frais scolaires modifiés.')
            return redirect('finances:frais_list')
    else:
        form = FraisScolaireForm(instance=frais)
    return render(request, 'finances/frais_form.html', {'form': form})


@login_required
def paiement_list(request):
    if not request.user.has_module_permission('paiements', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    paiements = Paiement.objects.select_related('eleve', 'frais').all().order_by('-date_paiement')[:100]
    return render(request, 'finances/paiement_list.html', {'paiements': paiements})


@login_required
def paiement_create(request, eleve_pk=None):
    if not request.user.has_module_permission('paiements', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    initial_data = {}
    if eleve_pk:
        from scolarite.models import Eleve
        eleve = get_object_or_404(Eleve, pk=eleve_pk)
        initial_data['eleve'] = eleve
        
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.encaisse_par = request.user
            paiement.save()
            messages.success(request, 'Paiement enregistré.')
            return redirect('finances:paiement_list')
    else:
        form = PaiementForm(initial=initial_data)
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
    from scolarite.models import Eleve
    eleve = get_object_or_404(Eleve, pk=eleve_pk)
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    inscriptions = eleve.inscriptions.select_related('classe', 'annee_scolaire').all()
    paiements = eleve.paiements.select_related('frais').all().order_by('-date_paiement')
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
    from scolarite.models import Eleve
    eleve = get_object_or_404(Eleve, pk=eleve_pk)
    paiements = eleve.paiements.select_related('frais').all().order_by('-date_paiement')
    return render(request, 'finances/historique_paiements.html', {'eleve': eleve, 'paiements': paiements})


@login_required
def gestion_salaires(request):
    if not request.user.has_module_permission('salaires_rh', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    # Récupérer toutes les années disponibles
    years = Salaire.objects.values_list('annee', flat=True).distinct().order_by('-annee')
    if not years:
        years = [date.today().year]
    
    # Filtrer par année si spécifiée
    annee_filter = request.GET.get('annee', '')
    salaires = Salaire.objects.select_related('personnel').all().order_by('-annee', '-mois')
    if annee_filter:
        salaires = salaires.filter(annee=annee_filter)
    
    return render(request, 'finances/salaire_list.html', {
        'salaires': salaires,
        'years': years,
        'annee_filter': annee_filter
    })


@login_required
def operation_caisse(request):
    if not request.user.has_module_permission('caisse', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    operations = OperationCaisse.objects.select_related('personnel').all().order_by('-date_operation')
    
    total_encaissements = operations.filter(type_operation='encaissement').aggregate(total=Sum('montant'))['total'] or 0
    total_decaissements = operations.filter(type_operation='decaissement').aggregate(total=Sum('montant'))['total'] or 0
    solde = total_encaissements - total_decaissements
    
    return render(request, 'finances/caisse.html', {
        'operations': operations,
        'total_encaissements': total_encaissements,
        'total_decaissements': total_decaissements,
        'solde': solde,
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
def charge_fixe_create(request):
    if not request.user.has_module_permission('charges', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('finances:charges_list')
    if request.method == 'POST':
        form = ChargeFixeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Charge fixe créée avec succès.')
            return redirect('finances:charges_list')
    else:
        form = ChargeFixeForm()
    return render(request, 'finances/charge_form.html', {'form': form, 'type': 'fixe'})


@login_required
def charge_fixe_edit(request, pk):
    if not request.user.has_module_permission('charges', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('finances:charges_list')
    charge = get_object_or_404(ChargeFixe, pk=pk)
    if request.method == 'POST':
        form = ChargeFixeForm(request.POST, instance=charge)
        if form.is_valid():
            form.save()
            messages.success(request, 'Charge fixe mise à jour.')
            return redirect('finances:charges_list')
    else:
        form = ChargeFixeForm(instance=charge)
    return render(request, 'finances/charge_form.html', {'form': form, 'charge': charge, 'type': 'fixe'})


@login_required
def charge_fixe_delete(request, pk):
    if not request.user.has_module_permission('charges', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('finances:charges_list')
    charge = get_object_or_404(ChargeFixe, pk=pk)
    if request.method == 'POST':
        charge.delete()
        messages.success(request, 'Charge fixe supprimée.')
        return redirect('finances:charges_list')
    return render(request, 'finances/charge_confirm_delete.html', {'charge': charge, 'type': 'fixe'})


@login_required
def charge_operationnelle_create(request):
    if not request.user.has_module_permission('charges', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('finances:charges_list')
    if request.method == 'POST':
        form = ChargeOperationnelleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Charge opérationnelle créée avec succès.')
            return redirect('finances:charges_list')
    else:
        form = ChargeOperationnelleForm()
    return render(request, 'finances/charge_form.html', {'form': form, 'type': 'operationnelle'})


@login_required
def charge_operationnelle_edit(request, pk):
    if not request.user.has_module_permission('charges', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('finances:charges_list')
    charge = get_object_or_404(ChargeOperationnelle, pk=pk)
    if request.method == 'POST':
        form = ChargeOperationnelleForm(request.POST, instance=charge)
        if form.is_valid():
            form.save()
            messages.success(request, 'Charge opérationnelle mise à jour.')
            return redirect('finances:charges_list')
    else:
        form = ChargeOperationnelleForm(instance=charge)
    return render(request, 'finances/charge_form.html', {'form': form, 'charge': charge, 'type': 'operationnelle'})


@login_required
def charge_operationnelle_delete(request, pk):
    if not request.user.has_module_permission('charges', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('finances:charges_list')
    charge = get_object_or_404(ChargeOperationnelle, pk=pk)
    if request.method == 'POST':
        charge.delete()
        messages.success(request, 'Charge opérationnelle supprimée.')
        return redirect('finances:charges_list')
    return render(request, 'finances/charge_confirm_delete.html', {'charge': charge, 'type': 'operationnelle'})


@login_required
def personnel_list(request):
    if not request.user.has_module_permission('personnel_rh', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    personnel_list = MembrePersonnel.objects.select_related('utilisateur').all().order_by('-date_embauche')
    total_salaires_mensuels = sum(p.salaire_base or 0 for p in personnel_list if p.est_actif)
    
    return render(request, 'finances/personnel_list.html', {
        'personnel_list': personnel_list,
        'total_salaires_mensuels': total_salaires_mensuels,
    })


@login_required
def tableau_bord_financier(request):
    if not request.user.has_module_permission('tableau_bord_financier', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    total_frais = _calculer_total_frais_avec_eleves(annee) if annee else 0
    
    paiements_query = Paiement.objects.all()
    if annee:
        paiements_query = paiements_query.filter(date_paiement__gte=annee.date_debut, date_paiement__lte=annee.date_fin)
        
    total_paiements = paiements_query.aggregate(total=Sum('montant'))['total'] or 0
    
    today = date.today()
    encaissements_mois = paiements_query.filter(
        date_paiement__month=today.month,
        date_paiement__year=today.year
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    total_salaires = Salaire.objects.filter(est_paye=True)
    if annee:
        total_salaires = total_salaires.filter(date_versement__gte=annee.date_debut, date_versement__lte=annee.date_fin)
    total_salaires = total_salaires.aggregate(total=Sum('salaire_net'))['total'] or 0
    
    total_decaissements = OperationCaisse.objects.filter(type_operation='decaissement')
    if annee:
        total_decaissements = total_decaissements.filter(date_operation__gte=annee.date_debut, date_operation__lte=annee.date_fin)
    total_decaissements = total_decaissements.aggregate(total=Sum('montant'))['total'] or 0
    
    total_charges = total_salaires + total_decaissements
    
    return render(request, 'finances/tableau_bord.html', {
        'annee': annee,
        'total_frais': total_frais,
        'total_paiements': total_paiements,
        'encaissements_mois': encaissements_mois,
        'total_charges': total_charges,
        'solde': total_paiements - total_charges,
        'taux_recouvrement': (total_paiements / total_frais * 100) if total_frais > 0 else 0,
    })


@login_required
def cycle_list(request):
    if not request.user.has_module_permission('cycles', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    cycles = Cycle.objects.all()
    return render(request, 'finances/cycle_list.html', {'cycles': cycles})


@login_required
def cycle_create(request):
    if not request.user.has_module_permission('cycles', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('finances:cycle_list')
    if request.method == 'POST':
        form = CycleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cycle créé avec succès.')
            return redirect('finances:cycle_list')
    else:
        form = CycleForm()
    return render(request, 'finances/cycle_form.html', {'form': form})


@login_required
def cycle_edit(request, pk):
    if not request.user.has_module_permission('cycles', 'update'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('finances:cycle_list')
    cycle = get_object_or_404(Cycle, pk=pk)
    if request.method == 'POST':
        form = CycleForm(request.POST, instance=cycle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cycle mis à jour.')
            return redirect('finances:cycle_list')
    else:
        form = CycleForm(instance=cycle)
    return render(request, 'finances/cycle_form.html', {'form': form, 'cycle': cycle})


@login_required
def cycle_delete(request, pk):
    if not request.user.has_module_permission('cycles', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('finances:cycle_list')
    cycle = get_object_or_404(Cycle, pk=pk)
    if request.method == 'POST':
        cycle.delete()
        messages.success(request, 'Cycle supprimé.')
        return redirect('finances:cycle_list')
    return render(request, 'finances/cycle_confirm_delete.html', {'cycle': cycle})


@login_required
def eleves_en_retard(request):
    if not request.user.has_module_permission('eleves_retard', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    
    from scolarite.models import EleveInscription
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    
    eleves_retard = []
    if annee:
        inscriptions = EleveInscription.objects.filter(annee_scolaire=annee).select_related('eleve', 'classe__niveau')
        
        for ins in inscriptions:
            # Simple check for demo purposes
            total_paye = Paiement.objects.filter(eleve=ins.eleve, frais__annee_scolaire=annee).aggregate(total=Sum('montant'))['total'] or 0
            # Logic for expected fees could be complex, for now we just show who hasn't paid anything
            if total_paye == 0:
                eleves_retard.append(ins)
    
    return render(request, 'finances/eleves_retard.html', {
        'eleves_retard': eleves_retard,
        'annee': annee
    })


@login_required
def facture_list(request):
    if not request.user.has_module_permission('factures', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    factures = Facture.objects.select_related('eleve').all().order_by('-date_facture')[:100]
    return render(request, 'finances/facture_list.html', {'factures': factures})


@login_required
def facture_create(request):
    messages.info(request, "Les factures sont générées automatiquement lors des paiements.")
    return redirect('finances:facture_list')


@login_required
def bourse_list(request):
    if not request.user.has_module_permission('bourses', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    bourses = BourseRemise.objects.all()
    return render(request, 'finances/bourse_list.html', {'bourses': bourses})


@login_required
def rapport_financier(request):
    if not request.user.has_module_permission('rapport_financier', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    return render(request, 'finances/rapport_financier.html')


@login_required
def rappel_list(request):
    if not request.user.has_module_permission('rappels', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation de voir les rappels.")
        return redirect('dashboard')
    
    annee = AnneeScolaire.objects.filter(est_active=True).first()
    eleves_en_retard = []
    
    if annee:
        inscriptions = EleveInscription.objects.filter(
            annee_scolaire=annee
        ).select_related('eleve', 'classe')
        
        for inscription in inscriptions:
            eleve = inscription.eleve
            total_frais = FraisScolaire.get_total_frais_classe(inscription.classe, annee)
            total_paye = Paiement.get_total_paye(eleve, annee)
            reste = total_frais - total_paye
            
            if reste > 0:
                eleves_en_retard.append({
                    'eleve': eleve,
                    'classe': inscription.classe,
                    'total_frais': total_frais,
                    'total_paye': total_paye,
                    'reste': reste
                })
    
    return render(request, 'finances/rappel_list.html', {
        'eleves_en_retard': eleves_en_retard,
        'annee': annee
    })
