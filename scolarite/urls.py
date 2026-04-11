from django.urls import path
from . import views

app_name = 'scolarite'

urlpatterns = [
    path('', views.eleve_list, name='eleve_list'),
    path('ajouter/', views.eleve_create, name='eleve_create'),
    path('<int:pk>/', views.eleve_detail, name='eleve_detail'),
    path('<int:pk>/modifier/', views.eleve_update, name='eleve_update'),
    path('<int:pk>/supprimer/', views.eleve_delete, name='eleve_delete'),
    
    path('parents/', views.parent_list, name='parent_list'),
    path('parents/ajouter/', views.parent_create, name='parent_create'),
    path('parents/ajouter/<int:eleve_id>/', views.parent_create, name='parent_create_eleve'),
    
    path('dossiers-medicaux/', views.dossiers_medical, name='dossiers_medical'),
    path('dossiers-medicaux/<int:eleve_id>/', views.dossier_medical_edit, name='dossier_medical_edit'),
    
    path('documents/', views.documents_eleve, name='documents_eleve'),
    path('documents/<int:eleve_id>/ajouter/', views.document_upload, name='document_upload'),
    path('documents/<int:pk>/supprimer/', views.document_delete, name='document_delete'),
    
    path('discipline/', views.discipline_list, name='discipline_list'),
    path('discipline/ajouter/', views.discipline_create, name='discipline_create'),
    path('discipline/<int:pk>/', views.discipline_detail, name='discipline_detail'),
    path('discipline/<int:pk>/modifier/', views.discipline_edit, name='discipline_edit'),
    path('discipline/<int:pk>/supprimer/', views.discipline_delete, name='discipline_delete'),
    path('discipline/<int:pk>/traiter/', views.discipline_treat, name='discipline_treat'),
    path('discipline/statistiques/', views.discipline_statistics, name='discipline_statistics'),
    path('discipline/historique/<int:eleve_id>/', views.discipline_history, name='discipline_history'),
    path('discipline/export/', views.discipline_export, name='discipline_export'),
    path('discipline/batch/', views.discipline_batch_treat, name='discipline_batch_treat'),
    
    path('conduite/config/', views.conduite_config_list, name='conduite_config_list'),
    path('conduite/config/<str:niveau>/', views.conduite_config_edit, name='conduite_config_edit'),
    
    path('periodes/cloture/', views.periode_cloture_list, name='periode_cloture_list'),
    path('periodes/cloture/<int:classe_id>/', views.periode_cloture_edit, name='periode_cloture_edit'),
    path('periodes/cloture/<int:classe_id>/<int:periode>/supprimer/', views.periode_cloture_delete, name='periode_cloture_delete'),
    
    path('notes/cloture/', views.note_cloture_list, name='note_cloture_list'),
    path('notes/cloture/<int:classe_id>/', views.note_cloture_edit, name='note_cloture_edit'),
]
