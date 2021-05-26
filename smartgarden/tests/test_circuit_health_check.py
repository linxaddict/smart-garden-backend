import datetime

import pytz
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from smartgarden.commons.asserts import CommonAsserts
from smartgarden.commons.fixtures import create_user, create_circuit
from smartgarden.models import Circuit
from smartgarden.views import ControlledCircuitHealthCheckView


class ControlledCircuitHealthCheckViewTest(APITestCase, CommonAsserts):
    def setUp(self):
        self.user = create_user()
        self.view = ControlledCircuitHealthCheckView.as_view()
        self.factory = APIRequestFactory()
        self.url = reverse('mine-circuit-health')

    def test_patch(self):
        health_check = datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(days=1)
        circuit = create_circuit(name='c1', controller=self.user, health_check=health_check)
        healthy = circuit.healthy

        self.assertFalse(healthy)

        request = self.factory.patch(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCircuitEqual(response.data, Circuit.objects.get(pk=circuit.pk))

    def test_patch_unauthenticated(self):
        request = self.factory.patch(self.url, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
