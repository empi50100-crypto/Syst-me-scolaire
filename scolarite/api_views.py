from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Eleve, ParentTuteur, EleveInscription, SanctionRecompense, DocumentEleve
from .serializers import (
    EleveSerializer, ParentTuteurSerializer, EleveInscriptionSerializer,
    SanctionRecompenseSerializer, DocumentEleveSerializer
)


class EleveViewSet(viewsets.ModelViewSet):
    queryset = Eleve.objects.all()
    serializer_class = EleveSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sexe', 'statut']
    
    def get_queryset(self):
        if self.request.user.role == 'professeur' and hasattr(self.request.user, 'profil_professeur'):
            return Eleve.objects.filter(inscriptions__classe__attributions__professeur=self.request.user.profil_professeur).distinct()
        return Eleve.objects.all()


class ParentTuteurViewSet(viewsets.ModelViewSet):
    queryset = ParentTuteur.objects.all()
    serializer_class = ParentTuteurSerializer
    permission_classes = [permissions.IsAuthenticated]


class EleveInscriptionViewSet(viewsets.ModelViewSet):
    queryset = EleveInscription.objects.all()
    serializer_class = EleveInscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['annee_scolaire', 'classe']


class SanctionRecompenseViewSet(viewsets.ModelViewSet):
    queryset = SanctionRecompense.objects.all()
    serializer_class = SanctionRecompenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'type']


class DocumentEleveViewSet(viewsets.ModelViewSet):
    queryset = DocumentEleve.objects.all()
    serializer_class = DocumentEleveSerializer
    permission_classes = [permissions.IsAuthenticated]
