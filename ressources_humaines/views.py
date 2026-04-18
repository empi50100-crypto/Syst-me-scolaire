from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import MembrePersonnel, Salaire, FichePoste, ContratEmploye
from .forms import MembrePersonnelForm, SalaireForm, FichePosteForm, ContratEmployeForm


@login_required
def liste_personnel(request):
    if not request.user.has_module_permission('personnel_list', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    fonction_filter = request.GET.get('fonction')
    personnel_list = MembrePersonnel.objects.select_related('utilisateur', 'poste').all()
    
    if fonction_filter:
        personnel_list = personnel_list.filter(fonction=fonction_filter)
    
    total_actif = personnel_list.filter(est_actif=True).count()
    
    paginator = Paginator(personnel_list, 20)
    page = request.GET.get('page')
    personnel = paginator.get_page(page)
    
    return render(request, 'ressources_humaines/personnel_list.html', {
        'personnel': personnel,
        'fonction_filter': fonction_filter,
        'total_actif': total_actif,
    })


@login_required
def creer_personnel(request):
    if not request.user.has_module_permission('personnel_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('ressources_humaines:liste_personnel')
    if request.method == 'POST':
        form = MembrePersonnelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membre du personnel créé avec succès.')
            return redirect('ressources_humaines:liste_personnel')
    else:
        form = MembrePersonnelForm()
    return render(request, 'ressources_humaines/personnel_form.html', {'form': form})


@login_required
def modifier_personnel(request, pk):
    if not request.user.has_module_permission('personnel_list', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('ressources_humaines:liste_personnel')
    personnel = get_object_or_404(MembrePersonnel, pk=pk)
    if request.method == 'POST':
        form = MembrePersonnelForm(request.POST, instance=personnel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membre du personnel modifié avec succès.')
            return redirect('ressources_humaines:liste_personnel')
    else:
        form = MembrePersonnelForm(instance=personnel)
    return render(request, 'ressources_humaines/personnel_form.html', {'form': form, 'personnel': personnel})


@login_required
def supprimer_personnel(request, pk):
    if not request.user.has_module_permission('personnel_list', 'delete'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('ressources_humaines:liste_personnel')
    personnel = get_object_or_404(MembrePersonnel, pk=pk)
    if request.method == 'POST':
        personnel.delete()
        messages.success(request, 'Membre du personnel supprimé avec succès.')
        return redirect('ressources_humaines:liste_personnel')
    return render(request, 'ressources_humaines/personnel_confirm_delete.html', {'personnel': personnel})


@login_required
def liste_salaires(request):
    if not request.user.has_module_permission('salaires', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    annee_filter = request.GET.get('annee')
    employe_filter = request.GET.get('employe')
    
    salaires_list = Salaire.objects.select_related('employe__utilisateur').order_by('-annee', '-mois')
    
    if annee_filter:
        salaires_list = salaires_list.filter(annee=int(annee_filter))
    if employe_filter:
        salaires_list = salaires_list.filter(employe_id=int(employe_filter))
    
    total_net = salaires_list.aggregate(total=Sum('salaire_net'))['total'] or 0
    nb_payes = salaires_list.filter(est_paye=True).count()
    
    paginator = Paginator(salaires_list, 20)
    page = request.GET.get('page')
    salaires = paginator.get_page(page)
    
    return render(request, 'ressources_humaines/salaires_list.html', {
        'salaires': salaires,
        'annee_filter': annee_filter,
        'employe_filter': employe_filter,
        'total_net': total_net,
        'nb_payes': nb_payes,
    })


@login_required
def creer_salaire(request):
    if not request.user.has_module_permission('salaires', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('ressources_humaines:liste_salaires')
    if request.method == 'POST':
        form = SalaireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salaire enregistré avec succès.')
            return redirect('ressources_humaines:liste_salaires')
    else:
        form = SalaireForm()
        employe_id = request.GET.get('employe')
        if employe_id:
            form.fields['employe'].initial = employe_id
    return render(request, 'ressources_humaines/salaire_form.html', {'form': form})


@login_required
def detail_salaire(request, pk):
    if not request.user.has_module_permission('salaires', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    salaire = get_object_or_404(Salaire, pk=pk)
    return render(request, 'ressources_humaines/salaire_detail.html', {'salaire': salaire})


@login_required
def liste_postes(request):
    if not request.user.has_module_permission('postes', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    postes = FichePoste.objects.all().order_by('-est_active', '-date_creation')
    return render(request, 'ressources_humaines/postes_list.html', {'postes': postes})


@login_required
def creer_poste(request):
    if not request.user.has_module_permission('postes', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('ressources_humaines:liste_postes')
    if request.method == 'POST':
        form = FichePosteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Poste créé avec succès.')
            return redirect('ressources_humaines:liste_postes')
    else:
        form = FichePosteForm()
    return render(request, 'ressources_humaines/poste_form.html', {'form': form})


@login_required
def modifier_poste(request, pk):
    if not request.user.has_module_permission('postes', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('ressources_humaines:liste_postes')
    poste = get_object_or_404(FichePoste, pk=pk)
    if request.method == 'POST':
        form = FichePosteForm(request.POST, instance=poste)
        if form.is_valid():
            form.save()
            messages.success(request, 'Poste modifié avec succès.')
            return redirect('ressources_humaines:liste_postes')
    else:
        form = FichePosteForm(instance=poste)
    return render(request, 'ressources_humaines/poste_form.html', {'form': form, 'poste': poste})


@login_required
def liste_contrats(request):
    if not request.user.has_module_permission('contrats', 'read'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard')
    statut_filter = request.GET.get('statut')
    contrats = ContratEmploye.objects.select_related('employe__utilisateur', 'poste').order_by('-date_debut')
    
    if statut_filter:
        contrats = contrats.filter(statut=statut_filter)
    
    return render(request, 'ressources_humaines/contrats_list.html', {'contrats': contrats, 'statut_filter': statut_filter})


@login_required
def creer_contrat(request):
    if not request.user.has_module_permission('contrats', 'write'):
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('ressources_humaines:liste_contrats')
    if request.method == 'POST':
        form = ContratEmployeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrat créé avec succès.')
            return redirect('ressources_humaines:liste_contrats')
    else:
        form = ContratEmployeForm()
    return render(request, 'ressources_humaines/contrat_form.html', {'form': form})
