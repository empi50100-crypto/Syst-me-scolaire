from django.urls import path
from . import views

app_name = 'enseignement'

urlpatterns = [
    path('classes/', views.classe_list_view, name='classe_list'),
    path('classes/ajouter/', views.classe_create_view, name='classe_create'),
    path('classes/<int:pk>/modifier/', views.classe_edit_view, name='classe_edit'),
    path('classes/<int:pk>/supprimer/', views.classe_delete_view, name='classe_delete'),
    
    path('matieres/', views.matiere_list_view, name='matiere_list'),
    path('matieres/ajouter/', views.matiere_create_view, name='matiere_create'),
    path('matieres/<int:pk>/modifier/', views.matiere_edit_view, name='matiere_edit'),
    path('matieres/<int:pk>/supprimer/', views.matiere_delete_view, name='matiere_delete'),
    
    path('professeurs/', views.professeur_list_view, name='professeur_list'),
    path('professeurs/ajouter/', views.professeur_create_view, name='professeur_create'),
    
    path('attributions/', views.attribution_list_view, name='attribution_list'),
    path('attributions/ajouter/', views.attribution_create_view, name='attribution_create'),
    
    path('salles/', views.salle_list_view, name='salle_list'),
    path('examens/', views.examen_list, name='examen_list'),
    path('contraintes/', views.contrainte_list, name='contrainte_list'),
    path('emploi-du-temps/', views.emploi_du_temps, name='emploi_du_temps'),
    
    path('mes-classes/', views.mes_classes_view, name='mes_classes'),
    path('saisie-notes/', views.saisie_notes, name='saisie_notes'),
    path('saisie-notes/<int:classe_pk>/<int:matiere_pk>/', views.saisie_notes_detail_view, name='saisie_notes_detail'),
]
