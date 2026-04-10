from django.urls import path
from . import views

app_name = 'finances'

urlpatterns = [
    path('annees/', views.annee_list, name='annee_list'),
    path('annees/ajouter/', views.annee_create, name='annee_create'),
    path('annees/<int:pk>/modifier/', views.annee_edit, name='annee_edit'),
    path('annees/<int:pk>/supprimer/', views.annee_delete, name='annee_delete'),
    path('annees/<int:pk>/activer/', views.annee_activer, name='annee_activer'),
    path('annees/<int:pk>/selectionner/', views.annee_selectionner, name='annee_selectionner'),
    path('frais/', views.frais_list, name='frais_list'),
    path('frais/ajouter/', views.frais_create, name='frais_create'),
    path('frais/<int:pk>/modifier/', views.frais_update, name='frais_update'),
    path('paiements/', views.paiement_list, name='paiement_list'),
    path('paiements/<int:paiement_pk>/recu/', views.recu_paiement, name='recu_paiement'),
    path('paiements/ajouter/', views.paiement_create, name='paiement_create'),
    path('paiements/ajouter/<int:eleve_pk>/', views.paiement_create, name='paiement_create_eleve'),
    path('eleve/<int:eleve_pk>/compte/', views.etat_compte_eleve, name='etat_compte_eleve'),
    path('eleve/<int:eleve_pk>/paiements/', views.historique_paiements_eleve, name='historique_paiements_eleve'),
    path('salaires/', views.gestion_salaires, name='gestion_salaires'),
    path('salaires/ajouter/', views.salaire_create, name='salaire_create'),
    path('caisse/', views.operation_caisse, name='operation_caisse'),
    path('charges/', views.charges_list, name='charges_list'),
    path('personnel/', views.personnel_list, name='personnel_list'),
    path('personnel/ajouter/', views.personnel_create, name='personnel_create'),
    path('personnel/<int:pk>/modifier/', views.personnel_edit, name='personnel_edit'),
    path('personnel/<int:pk>/supprimer/', views.personnel_delete, name='personnel_delete'),
    path('charges/fixe/ajouter/', views.charge_fixe_create, name='charge_fixe_create'),
    path('charges/fixe/<int:pk>/modifier/', views.charge_fixe_edit, name='charge_fixe_edit'),
    path('charges/fixe/<int:pk>/supprimer/', views.charge_fixe_delete, name='charge_fixe_delete'),
    path('charges/operationnelle/ajouter/', views.charge_operationnelle_create, name='charge_operationnelle_create'),
    path('charges/operationnelle/<int:pk>/supprimer/', views.charge_operationnelle_delete, name='charge_operationnelle_delete'),
    path('tableau-bord/', views.tableau_bord_financier, name='tableau_bord_financier'),
    path('rappels/', views.liste_rappels, name='liste_rappels'),
    path('generer-rappels/', views.generer_rappels, name='generer_rappels'),
    path('cycles/', views.cycle_list, name='cycle_list'),
    path('cycles/ajouter/', views.cycle_create, name='cycle_create'),
    path('cycles/<int:pk>/', views.cycle_edit, name='cycle_edit'),
    path('cycles/<int:pk>/supprimer/', views.cycle_delete, name='cycle_delete'),
    path('eleves-en-retard/', views.eleves_en_retard, name='eleves_en_retard'),
    
    path('factures/', views.facture_list, name='facture_list'),
    path('factures/ajouter/', views.facture_create, name='facture_create'),
    path('factures/<int:pk>/', views.facture_detail, name='facture_detail'),
    path('factures/<int:pk>/pdf/', views.facture_pdf, name='facture_pdf'),
    
    path('bourses/', views.bourse_list, name='bourse_list'),
    path('bourses/ajouter/', views.bourse_create, name='bourse_create'),
    
    path('categories-depense/', views.categorie_depense, name='categorie_depense'),
    
    path('rapport-financier/', views.rapport_financier, name='rapport_financier'),
]
