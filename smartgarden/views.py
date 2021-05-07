import datetime

from django.db.models import Prefetch
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from smartgarden.models import Circuit, User, ScheduledOneTimeActivation
from smartgarden.serializers import UserSerializer, CircuitSerializer
from smartgarden.view_models import CircuitViewModel


def index(request):
    context = {
        'circuits': [CircuitViewModel(c) for c in Circuit.objects.all()]
    }
    return render(request, 'smartgarden/circuits.html', context)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User \
        .objects \
        .select_related('controlled_circuit') \
        .all()

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class CircuitViewSet(viewsets.ReadOnlyModelViewSet):
    today_one_time_activations = ScheduledOneTimeActivation \
        .objects \
        .filter(timestamp__date=datetime.date.today()) \
        .order_by('-timestamp')

    one_time_activations_prefetch = Prefetch('one_time_activations', today_one_time_activations)

    queryset = Circuit \
        .objects \
        .select_related('controller') \
        .prefetch_related(one_time_activations_prefetch) \
        .prefetch_related('schedule') \
        .all()

    serializer_class = CircuitSerializer


class ControlledCircuit(RetrieveAPIView):
    serializer_class = CircuitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=request.user.pk)
            circuit = user.controlled_circuit
            serializer = self.serializer_class(circuit, many=False)

            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Circuit.DoesNotExist:
            raise NotFound(detail="circuit not assigned", code=404)
