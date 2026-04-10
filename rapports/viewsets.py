from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from accounts.models import User
from eleves.models import Eleve, Inscription
from academics.models import Classe, Matiere, Professeur, Enseignement, Evaluation
from finances.models import AnneeScolaire, FraisScolaire, Paiement, Salaire
from presences.models import Presence, Appel
from .serializers import (
    UserSerializer, EleveSerializer, InscriptionSerializer,
    ClasseSerializer, MatiereSerializer, ProfesseurSerializer,
    EnseignementSerializer, EvaluationSerializer, AnneeScolaireSerializer, 
    FraisScolaireSerializer, PaiementSerializer, PresenceSerializer, SalaireSerializer
)


class IsDirectionOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_direction()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name']


class EleveViewSet(viewsets.ModelViewSet):
    queryset = Eleve.objects.all()
    serializer_class = EleveSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['statut', 'sexe']
    search_fields = ['matricule', 'nom', 'prenom']
    
    @action(detail=True, methods=['get'])
    def inscriptions(self, request, pk=None):
        eleve = self.get_object()
        inscriptions = eleve.inscriptions.all()
        serializer = InscriptionSerializer(inscriptions, many=True)
        return Response(serializer.data)


class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['annee_scolaire', 'classe']


class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirectionOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['niveau', 'annee_scolaire']
    search_fields = ['nom']
    
    @action(detail=True, methods=['get'])
    def eleves(self, request, pk=None):
        classe = self.get_object()
        inscriptions = classe.inscriptions.filter(annee_scolaire__est_active=True)
        serializer = InscriptionSerializer(inscriptions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def matieres(self, request, pk=None):
        classe = self.get_object()
        matieres = classe.matieres.all()
        serializer = MatiereSerializer(matieres, many=True)
        return Response(serializer.data)


class MatiereViewSet(viewsets.ModelViewSet):
    queryset = Matiere.objects.all()
    serializer_class = MatiereSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirectionOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['classe']


class ProfesseurViewSet(viewsets.ModelViewSet):
    queryset = Professeur.objects.all()
    serializer_class = ProfesseurSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirectionOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['statut']
    search_fields = ['nom', 'prenom']
    
    @action(detail=True, methods=['get'])
    def enseignements(self, request, pk=None):
        professeur = self.get_object()
        enseignements = professeur.enseignants.all()
        serializer = self.get_serializer(enseignements, many=True)
        return Response(serializer.data)


class EnseignementViewSet(viewsets.ModelViewSet):
    queryset = Enseignement.objects.all()
    serializer_class = EnseignementSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirectionOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['professeur', 'classe', 'annee_scolaire']


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['eleve', 'matiere', 'type_eval', 'annee_scolaire']
    ordering_fields = ['date_eval', 'note']
    
    @action(detail=False, methods=['get'])
    def by_classe(self, request):
        classe_id = request.query_params.get('classe')
        matiere_id = request.query_params.get('matiere')
        
        evaluations = Evaluation.objects.filter(
            matiere__classe_id=classe_id,
            matiere_id=matiere_id
        ).select_related('eleve')
        
        serializer = self.get_serializer(evaluations, many=True)
        return Response(serializer.data)


class AnneeScolaireViewSet(viewsets.ModelViewSet):
    queryset = AnneeScolaire.objects.all()
    serializer_class = AnneeScolaireSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirectionOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        annee = AnneeScolaire.objects.filter(est_active=True).first()
        if annee:
            serializer = self.get_serializer(annee)
            return Response(serializer.data)
        return Response({'detail': 'Aucune année active'}, status=404)


class FraisScolaireViewSet(viewsets.ModelViewSet):
    queryset = FraisScolaire.objects.all()
    serializer_class = FraisScolaireSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirectionOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['classe', 'annee_scolaire', 'type_frais']


class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['eleve', 'frais', 'mode_paiement']
    ordering_fields = ['date_paiement']
    
    @action(detail=False, methods=['get'])
    def eleve(self, request, pk=None):
        eleve_id = request.query_params.get('eleve')
        paiements = Paiement.objects.filter(eleve_id=eleve_id)
        serializer = self.get_serializer(paiements, many=True)
        return Response(serializer.data)


class PresenceViewSet(viewsets.ModelViewSet):
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['eleve', 'classe', 'statut', 'justifie']
    ordering_fields = ['date']
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        classe_id = request.query_params.get('classe')
        
        queryset = self.get_queryset()
        if classe_id:
            queryset = queryset.filter(classe_id=classe_id)
        
        total = queryset.count()
        presents = queryset.filter(statut='present').count()
        absents = queryset.filter(statut='absent').count()
        retards = queryset.filter(statut='retard').count()
        
        return Response({
            'total': total,
            'presents': presents,
            'absents': absents,
            'retards': retards,
            'taux_presence': round((presents / total * 100) if total > 0 else 100, 2)
        })


class SalaireViewSet(viewsets.ModelViewSet):
    queryset = Salaire.objects.all()
    serializer_class = SalaireSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirectionOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['personnel', 'annee', 'statut']
