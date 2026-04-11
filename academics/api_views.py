from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Classe, Matiere, Enseignement, Evaluation, Salle, Examen, FicheNote
from .serializers import (
    ClasseSerializer, MatiereSerializer, EnseignementSerializer,
    EvaluationSerializer, SalleSerializer, ExamenSerializer, FicheNoteSerializer
)


class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['niveau', 'filiere', 'annee_scolaire']


class MatiereViewSet(viewsets.ModelViewSet):
    queryset = Matiere.objects.all()
    serializer_class = MatiereSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['classe']


class EnseignementViewSet(viewsets.ModelViewSet):
    queryset = Enseignement.objects.all()
    serializer_class = EnseignementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['classe', 'professeur', 'matiere']


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'matiere', 'type_evaluation']


class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type_salle']


class ExamenViewSet(viewsets.ModelViewSet):
    queryset = Examen.objects.all()
    serializer_class = ExamenSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['classe', 'matiere', 'date_examen']


class FicheNoteViewSet(viewsets.ModelViewSet):
    queryset = FicheNote.objects.all()
    serializer_class = FicheNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'classe', 'periode']