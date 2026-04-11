from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Eleve, ParentTuteur, Inscription, DisciplineEleve, DocumentEleve
from .serializers import (
    EleveSerializer, ParentTuteurSerializer, InscriptionSerializer,
    DisciplineEleveSerializer, DocumentEleveSerializer
)


class EleveViewSet(viewsets.ModelViewSet):
    queryset = Eleve.objects.all()
    serializer_class = EleveSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sexe', 'statut', 'classe']
    
    def get_queryset(self):
        if self.request.user.is_professeur():
            return Eleve.objects.filter(classe__in=self.request.user.professeur.classes.all())
        return Eleve.objects.all()


class ParentTuteurViewSet(viewsets.ModelViewSet):
    queryset = ParentTuteur.objects.all()
    serializer_class = ParentTuteurSerializer
    permission_classes = [permissions.IsAuthenticated]


class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['annee_scolaire', 'classe', 'statut']


class DisciplineEleveViewSet(viewsets.ModelViewSet):
    queryset = DisciplineEleve.objects.all()
    serializer_class = DisciplineEleveSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'type_incident', 'gravite']


class DocumentEleveViewSet(viewsets.ModelViewSet):
    queryset = DocumentEleve.objects.all()
    serializer_class = DocumentEleveSerializer
    permission_classes = [permissions.IsAuthenticated]