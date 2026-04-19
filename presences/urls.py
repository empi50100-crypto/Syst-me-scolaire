from django.urls import path
from . import views

app_name = 'presences'

urlpatterns = [
    path('', views.presence_list, name='presence_list'),
    path('appel/<int:classe_pk>/', views.faire_appel, name='faire_appel'),
    path('rapport-retards/', views.rapport_retards, name='rapport_retards'),
    path('statistiques/', views.statistiques_presence, name='statistiques_presence'),
    path('mes-seances/', views.mes_seances, name='mes_seances'),
    path('seances/demarrer/<int:attribution_id>/', views.demarrer_seance, name='demarrer_seance'),
    path('seances/terminer/<int:seance_id>/', views.terminer_seance, name='terminer_seance'),
    path('seances/', views.liste_seances, name='liste_seances'),
    path('attestation/', views.attestation_assiduite_form, name='attestation_assiduite_form'),
    path('attestation/<int:eleve_pk>/pdf/', views.attestation_assiduite_pdf, name='attestation_assiduite_pdf'),
]
