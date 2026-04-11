from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    EleveViewSet, ParentTuteurViewSet, EleveInscriptionViewSet,
    SanctionRecompenseViewSet, DocumentEleveViewSet
)

router = DefaultRouter()
router.register(r'eleves', EleveViewSet, basename='eleve')
router.register(r'parents', ParentTuteurViewSet, basename='parent')
router.register(r'inscriptions', EleveInscriptionViewSet, basename='inscription')
router.register(r'disciplines', SanctionRecompenseViewSet, basename='discipline')
router.register(r'documents', DocumentEleveViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
]
