from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    EleveViewSet, ParentTuteurViewSet, InscriptionViewSet,
    DisciplineEleveViewSet, DocumentEleveViewSet
)

router = DefaultRouter()
router.register(r'eleves', EleveViewSet, basename='eleve')
router.register(r'parents', ParentTuteurViewSet, basename='parent')
router.register(r'inscriptions', InscriptionViewSet, basename='inscription')
router.register(r'disciplines', DisciplineEleveViewSet, basename='discipline')
router.register(r'documents', DocumentEleveViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
]