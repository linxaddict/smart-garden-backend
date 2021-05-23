from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from smartgarden.commons.asserts import CommonAsserts
from smartgarden.commons.fixtures import create_user, create_circuit
from smartgarden.views import ControlledCircuitView


class ControlledCircuitViewTest(APITestCase, CommonAsserts):
    def setUp(self):
        self.user = create_user()
        self.view = ControlledCircuitView.as_view()
        self.factory = APIRequestFactory()
        self.url = reverse('mine-circuit')

    def test_fetched_controlled_circuit_owner_is_the_controller(self):
        circuit = create_circuit(name='c1', controller=self.user)

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request)

        self.assertCircuitEqual(response.data, circuit)

    def test_fetched_controlled_circuit_owner_is_not_the_controller(self):
        controller = create_user(email='controller@test.com')
        circuit = create_circuit(name='c1', controller=controller)

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, controller)
        response = self.view(request)

        self.assertCircuitEqual(response.data, circuit)

    def test_fetched_controlled_circuit_no_circuit_assigned(self):
        create_circuit(name='c1')

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_fetched_controlled_circuit_unauthenticated(self):
        create_circuit(name='c1')

        request = self.factory.get(self.url, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
