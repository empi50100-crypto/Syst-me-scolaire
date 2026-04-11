from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from finances.models import (
    AnneeScolaire, FraisScolaire, Paiement, EcoleCompte, Salaire,
    ChargeFixe, ChargeOperationnelle, Personnel, Facture, BourseRemise
)
from finances.serializers import (
    AnneeScolaireSerializer, FraisScolaireSerializer, PaiementSerializer,
    EcoleCompteSerializer, SalaireSerializer, ChargeFixeSerializer,
    ChargeOperationnelleSerializer, PersonnelSerializer, FactureSerializer,
    BourseRemiseSerializer
)


class AnneeScolaireViewSet(viewsets.ModelViewSet):
    queryset = AnneeScolaire.objects.all()
    serializer_class = AnneeScolaireSerializer
    permission_classes = [permissions.IsAuthenticated]


class FraisScolaireViewSet(viewsets.ModelViewSet):
    queryset = FraisScolaire.objects.all()
    serializer_class = FraisScolaireSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['annee_scolaire', 'classe', 'type_frais']


class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'annee_scolaire', 'mode_paiement']


class EcoleCompteViewSet(viewsets.ModelViewSet):
    queryset = EcoleCompte.objects.all()
    serializer_class = EcoleCompteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type_operation', 'date_operation']


class SalaireViewSet(viewsets.ModelViewSet):
    queryset = Salaire.objects.all()
    serializer_class = SalaireSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employe', 'annee', 'est_paye']


class ChargeFixeViewSet(viewsets.ModelViewSet):
    queryset = ChargeFixe.objects.all()
    serializer_class = ChargeFixeSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChargeOperationnelleViewSet(viewsets.ModelViewSet):
    queryset = ChargeOperationnelle.objects.all()
    serializer_class = ChargeOperationnelleSerializer
    permission_classes = [permissions.IsAuthenticated]


class PersonnelViewSet(viewsets.ModelViewSet):
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['fonction', 'est_actif']


class FactureViewSet(viewsets.ModelViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['eleve', 'statut']


class BourseRemiseViewSet(viewsets.ModelViewSet):
    queryset = BourseRemise.objects.all()
    serializer_class = BourseRemiseSerializer
    permission_classes = [permissions.IsAuthenticated]