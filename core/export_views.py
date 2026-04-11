from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from eleves.models import Eleve
from finances.models import Paiement, Personnel
from core.export_utils import export_eleves, export_paiements, export_personnel


@login_required
def export_eleves_excel(request):
    if not request.user.has_module_permission('eleve_list', 'read'):
        return HttpResponse("Unauthorized", status=403)
    
    eleves = Eleve.objects.select_related('classe').all()
    return export_eleves(request, eleves)


@login_required
def export_paiements_excel(request):
    if not request.user.has_module_permission('paiements', 'read'):
        return HttpResponse("Unauthorized", status=403)
    
    annee = request.GET.get('annee')
    paiements = Paiement.objects.select_related('eleve').all()
    if annee:
        paiements = paiements.filter(date_paiement__year=int(annee))
    
    return export_paiements(request, paiements)


@login_required
def export_personnel_excel(request):
    if not request.user.has_module_permission('personnel_rh', 'read'):
        return HttpResponse("Unauthorized", status=403)
    
    personnel_list = Personnel.objects.all()
    return export_personnel(request, personnel_list)


@login_required
def export_view(request):
    """Page principale d'export"""
    return render(request, 'export.html')