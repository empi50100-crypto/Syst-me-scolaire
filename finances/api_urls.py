from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    AnneeScolaireViewSet, FraisScolaireViewSet, PaiementViewSet,
    EcoleCompteViewSet, SalaireViewSet, ChargeFixeViewSet,
    ChargeOperationnelleViewSet, PersonnelViewSet, FactureViewSet, BourseRemiseViewSet
)

router = DefaultRouter()
router.register(r'annees-scolaires', AnneeScolaireViewSet, basename='annee')
router.register(r'frais', FraisScolaireViewSet, basename='frais')
router.register(r'paiements', PaiementViewSet, basename='paiement')
router.register(r'compte', EcoleCompteViewSet, basename='compte')
router.register(r'salaires', SalaireViewSet, basename='salaire')
router.register(r'charges-fixes', ChargeFixeViewSet, basename='chargefixe')
router.register(r'charges-op', ChargeOperationnelleViewSet, basename='chargeop')
router.register(r'personnel', PersonnelViewSet, basename='personnel')
router.register(r'factures', FactureViewSet, basename='facture')
router.register(r'bourses', BourseRemiseViewSet, basename='bourse')

urlpatterns = [
    path('', include(router.urls)),
]