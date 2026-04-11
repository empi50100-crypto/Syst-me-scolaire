from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from authentification.models import Utilisateur
from scolarite.models import Eleve, EleveInscription
from enseignement.models import Classe, Matiere, ProfilProfesseur, Attribution, Evaluation
from core.models import AnneeScolaire
from finances.models import FraisScolaire, Paiement
from ressources_humaines.models import MembrePersonnel, Salaire
from presences.models import Presence, Appel
from .serializers import (
    UtilisateurSerializer, EleveSerializer, EleveInscriptionSerializer,
    ClasseSerializer, MatiereSerializer, ProfilProfesseurSerializer,
    AttributionSerializer, EvaluationSerializer, AnneeScolaireSerializer, 
    FraisScolaireSerializer, PaiementSerializer, PresenceSerializer, SalaireSerializer
)


class IsDirectionOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_direction()


class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name']


class EleveViewSet(viewsets.ModelViewSet):
    queryset = Eleve.objects.all()
    serializer_class = EleveSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['statut', 'sexe']
    search_fields = ['nom', 'prenom', 'matricule']


class EleveInscriptionViewSet(viewsets.ModelViewSet):
    queryset = EleveInscription.objects.all()
    serializer_class = EleveInscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['annee_scolaire', 'classe']


class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['annee_scolaire']


class MatiereViewSet(viewsets.ModelViewSet):
    queryset = Matiere.objects.all()
    serializer_class = MatiereSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProfilProfesseurViewSet(viewsets.ModelViewSet):
    queryset = ProfilProfesseur.objects.all()
    serializer_class = ProfilProfesseurSerializer
    permission_classes = [permissions.IsAuthenticated]


class AttributionViewSet(viewsets.ModelViewSet):
    queryset = Attribution.objects.all()
    serializer_class = AttributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['annee_scolaire', 'classe', 'professeur']


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'matiere']


class AnneeScolaireViewSet(viewsets.ModelViewSet):
    queryset = AnneeScolaire.objects.all()
    serializer_class = AnneeScolaireSerializer
    permission_classes = [permissions.IsAuthenticated]


class FraisScolaireViewSet(viewsets.ModelViewSet):
    queryset = FraisScolaire.objects.all()
    serializer_class = FraisScolaireSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['annee_scolaire', 'classe']


class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'frais']


class PresenceViewSet(viewsets.ModelViewSet):
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'classe', 'date']


class SalaireViewSet(viewsets.ModelViewSet):
    queryset = Salaire.objects.all()
    serializer_class = SalaireSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employe', 'mois', 'annee']
