from django.urls import path
from . import views

app_name = 'ressources_humaines'

urlpatterns = [
    path('', views.liste_personnel, name='liste_personnel'),
    path('creer/', views.creer_personnel, name='creer_personnel'),
    path('<int:pk>/modifier/', views.modifier_personnel, name='modifier_personnel'),
    path('<int:pk>/supprimer/', views.supprimer_personnel, name='supprimer_personnel'),
    path('salaires/', views.liste_salaires, name='liste_salaires'),
    path('salaires/creer/', views.creer_salaire, name='creer_salaire'),
    path('salaires/<int:pk>/', views.detail_salaire, name='detail_salaire'),
    path('postes/', views.liste_postes, name='liste_postes'),
    path('postes/creer/', views.creer_poste, name='creer_poste'),
    path('postes/<int:pk>/modifier/', views.modifier_poste, name='modifier_poste'),
    path('contrats/', views.liste_contrats, name='liste_contrats'),
    path('contrats/creer/', views.creer_contrat, name='creer_contrat'),
]
