from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ClasseViewSet, MatiereViewSet, EnseignementViewSet,
    EvaluationViewSet, SalleViewSet, ExamenViewSet, FicheNoteViewSet
)

router = DefaultRouter()
router.register(r'classes', ClasseViewSet, basename='classe')
router.register(r'matieres', MatiereViewSet, basename='matiere')
router.register(r'enseignements', EnseignementViewSet, basename='seignement')
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')
router.register(r'salles', SalleViewSet, basename='salle')
router.register(r'examen', ExamenViewSet, basename='examen')
router.register(r'fiches-notes', FicheNoteViewSet, basename='fichenote')

urlpatterns = [
    path('', include(router.urls)),
]