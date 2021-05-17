from smartgarden.models import Circuit


class ExtractCircuitMixin:
    @property
    def circuit_id(self):
        return self.kwargs[self.lookup_field]

    @property
    def circuit(self):
        return Circuit.objects.get(pk=self.circuit_id)
