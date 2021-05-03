from django.shortcuts import render

from smartgarden.models import Circuit
from smartgarden.view_models import CircuitViewModel


def index(request):
    context = {
        'circuits': [CircuitViewModel(c) for c in Circuit.objects.all()]
    }
    return render(request, 'smartgarden/circuits.html', context)
