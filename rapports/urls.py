from django.urls import path
from . import views

app_name = 'rapports'

urlpatterns = [
    path('bulletins/', views.bulletin_list, name='bulletin_list'),
    path('bulletin/classe/<int:classe_pk>/', views.bulletins_par_classe, name='bulletins_par_classe'),
    path('bulletin/classe/<int:classe_pk>/<int:cycle_pk>/', views.bulletins_par_classe, name='bulletins_par_classe_cycle'),
    path('bulletin/generer/<int:inscription_pk>/', views.generer_bulletin, name='generer_bulletin'),
    path('bulletin/pdf/<int:bulletin_pk>/', views.exporter_bulletin_pdf, name='exporter_bulletin_pdf'),
    path('academique/', views.rapport_academique, name='rapport_academique'),
    path('financier/', views.rapport_financier, name='rapport_financier'),
    path('transition-annee/', views.transition_annee, name='transition_annee'),
]
