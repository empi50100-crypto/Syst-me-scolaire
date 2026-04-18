from django.urls import path
from . import views

app_name = 'finances'

urlpatterns = [
    path('annees/', views.annee_list, name='annee_list'),
    path('annees/ajouter/', views.annee_create, name='annee_create'),
    path('annees/<int:pk>/modifier/', views.annee_edit, name='annee_edit'),
    path('annees/<int:pk>/supprimer/', views.annee_delete, name='annee_delete'),
    path('annees/<int:pk>/activer/', views.annee_activer, name='annee_activer'),
    path('annees/<int:pk>/selectionner/', views.annee_activer, name='annee_selectionner'),
    
    path('frais/', views.frais_list, name='frais_list'),
    path('frais/ajouter/', views.frais_create, name='frais_create'),
    path('frais/<int:pk>/modifier/', views.frais_update, name='frais_update'),
    
    path('paiements/', views.paiement_list, name='paiement_list'),
    path('paiements/ajouter/', views.paiement_create, name='paiement_create'),
    path('paiements/ajouter/<int:eleve_pk>/', views.paiement_create, name='paiement_create_eleve'),
    path('paiements/<int:paiement_pk>/recu/', views.recu_paiement, name='recu_paiement'),
    
    path('eleve/<int:eleve_pk>/compte/', views.etat_compte_eleve, name='etat_compte_eleve'),
    path('eleve/<int:eleve_pk>/paiements/', views.historique_paiements_eleve, name='historique_paiements_eleve'),
    
    path('salaires/', views.gestion_salaires, name='gestion_salaires'),
    path('caisse/', views.operation_caisse, name='operation_caisse'),
    path('charges/', views.charges_list, name='charges_list'),
    path('personnel/', views.personnel_list, name='personnel_list'),
    
    path('tableau-bord/', views.tableau_bord_financier, name='tableau_bord_financier'),
    path('cycles/', views.cycle_list, name='cycle_list'),
    path('eleves-en-retard/', views.eleves_en_retard, name='eleves_en_retard'),
    path('factures/', views.facture_list, name='facture_list'),
    path('factures/creer/', views.facture_create, name='facture_create'),
    path('bourses/', views.bourse_list, name='bourse_list'),
    path('rapport-financier/', views.rapport_financier, name='rapport_financier'),
    path('rappels/', views.rappel_list, name='rappel_list'),
]
