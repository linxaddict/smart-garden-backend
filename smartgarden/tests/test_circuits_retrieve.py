from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from smartgarden.commons.asserts import CommonAsserts
from smartgarden.commons.fixtures import create_user, create_circuit, create_scheduled_one_time_activation, \
    create_scheduled_activation
from smartgarden.views import CircuitViewSet


class CircuitViewSetRetrieveTest(APITestCase, CommonAsserts):
    def setUp(self):
        self.user = create_user()
        self.circuit = create_circuit(name='c1')
        self.circuit.collaborators.add(self.user)
        self.circuit_not_related = create_circuit(name='c2')
        self.view = CircuitViewSet.as_view(actions={
            'get': 'retrieve'
        })
        self.factory = APIRequestFactory()
        self.url = reverse('circuit-detail', kwargs={'pk': self.circuit.pk})

    def test_fetch_unauthenticated(self):
        request = self.factory.get(self.url, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch(self):
        create_scheduled_one_time_activation(self.circuit)
        create_scheduled_one_time_activation(self.circuit)

        create_scheduled_activation(self.circuit)
        create_scheduled_activation(self.circuit)

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, pk=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCircuitEqual(response.data, self.circuit)

    def test_fetch_not_related(self):
        create_scheduled_one_time_activation(self.circuit)
        create_scheduled_one_time_activation(self.circuit)

        create_scheduled_activation(self.circuit)
        create_scheduled_activation(self.circuit)

        url = reverse('circuit-detail', kwargs={'pk': self.circuit_not_related.pk})
        request = self.factory.get(url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, pk=self.circuit_not_related.pk)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
