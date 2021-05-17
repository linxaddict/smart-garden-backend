import datetime

from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from smartgarden.mixins import ExtractCircuitMixin
from smartgarden.models import Circuit, User, ScheduledOneTimeActivation, ScheduledActivation
from smartgarden.permissions import IsCircuitOwnerOnUnsafeOperations
from smartgarden.serializers import CircuitSerializer, ScheduledActivationSerializer, \
    ScheduledOneTimeActivationSerializer
from smartgarden.view_models import CircuitViewModel


def index(request):
    context = {
        'circuits': [CircuitViewModel(c) for c in Circuit.objects.all()]
    }
    return render(request, 'smartgarden/circuits.html', context)


class CircuitViewSet(viewsets.ReadOnlyModelViewSet):
    today_one_time_activations = ScheduledOneTimeActivation \
        .objects \
        .filter(timestamp__date=datetime.date.today()) \
        .order_by('-timestamp')

    one_time_activations_prefetch = Prefetch('one_time_activations', today_one_time_activations)

    queryset = Circuit \
        .objects \
        .prefetch_related(one_time_activations_prefetch) \
        .prefetch_related('schedule') \
        .all()

    serializer_class = CircuitSerializer
    permission_classes = [AllowAny]


class ControlledCircuitView(RetrieveAPIView):
    serializer_class = CircuitSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=request.user.pk)
            circuit = user.controlled_circuit
            serializer = self.serializer_class(circuit, many=False)

            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Circuit.DoesNotExist:
            raise NotFound(detail="circuit not assigned", code=404)


class CircuitScheduleView(ListAPIView, UpdateAPIView, ExtractCircuitMixin):
    serializer_class = ScheduledActivationSerializer
    queryset = ScheduledActivation.objects.all()
    lookup_field = 'circuit_id'
    permission_classes = [IsAuthenticated & IsCircuitOwnerOnUnsafeOperations]

    def get_queryset(self):
        return self.queryset.filter(circuit_id=self.circuit_id).order_by('-time')

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.filter_queryset(self.get_queryset()),
            data=request.data,
            many=True
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.get_queryset().delete()

            for item in serializer.validated_data:
                item['circuit_id'] = self.circuit_id

            serializer.create(serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CircuitOneTimeActivationView(ListCreateAPIView, ExtractCircuitMixin):
    serializer_class = ScheduledOneTimeActivationSerializer
    queryset = ScheduledOneTimeActivation.objects.all()
    lookup_field = 'circuit_id'
    permission_classes = [IsAuthenticated & IsCircuitOwnerOnUnsafeOperations]

    def get_queryset(self):
        return self.queryset \
            .filter(circuit_id=self.circuit_id) \
            .filter(timestamp__date=datetime.date.today()) \
            .order_by('-timestamp')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            many=False
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.validated_data['circuit_id'] = self.circuit_id
            serializer.create(serializer.validated_data)

        return Response(serializer.data, status=status.HTTP_200_OK)
