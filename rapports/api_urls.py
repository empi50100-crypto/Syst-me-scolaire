from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .viewsets import (
    UtilisateurViewSet, EleveViewSet, EleveInscriptionViewSet,
    ClasseViewSet, MatiereViewSet, ProfilProfesseurViewSet,
    AttributionViewSet, EvaluationViewSet, AnneeScolaireViewSet,
    FraisScolaireViewSet, PaiementViewSet, PresenceViewSet, SalaireViewSet
)

router = DefaultRouter()
router.register(r'users', UtilisateurViewSet)
router.register(r'eleves', EleveViewSet)
router.register(r'inscriptions', EleveInscriptionViewSet)
router.register(r'classes', ClasseViewSet)
router.register(r'matieres', MatiereViewSet)
router.register(r'professeurs', ProfilProfesseurViewSet)
router.register(r'enseignements', AttributionViewSet)
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
