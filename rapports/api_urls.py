from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .viewsets import (
    UserViewSet, EleveViewSet, InscriptionViewSet,
    ClasseViewSet, MatiereViewSet, ProfesseurViewSet,
    EnseignementViewSet, EvaluationViewSet, AnneeScolaireViewSet,
    FraisScolaireViewSet, PaiementViewSet, PresenceViewSet, SalaireViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'eleves', EleveViewSet)
router.register(r'inscriptions', InscriptionViewSet)
router.register(r'classes', ClasseViewSet)
router.register(r'matieres', MatiereViewSet)
router.register(r'professeurs', ProfesseurViewSet)
router.register(r'enseignements', EnseignementViewSet)
router.register(r'evaluations', EvaluationViewSet)
router.register(r'annees', AnneeScolaireViewSet)
router.register(r'frais', FraisScolaireViewSet)
router.register(r'paiements', PaiementViewSet)
router.register(r'presences', PresenceViewSet)
router.register(r'salaires', SalaireViewSet)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
