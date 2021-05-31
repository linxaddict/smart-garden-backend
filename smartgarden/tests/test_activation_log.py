import datetime

import pytz
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from smartgarden.commons.asserts import CommonAsserts
from smartgarden.commons.fixtures import create_user, create_circuit
from smartgarden.views import ActivationLogView


class ActivationLogViewTest(APITestCase, CommonAsserts):
    def setUp(self):
        self.user = create_user()
        self.circuit = create_circuit(name='c1')
        self.circuit.controller = self.user
        self.circuit.save()

        self.view = ActivationLogView.as_view()
        self.factory = APIRequestFactory()
        self.url = reverse('circuit-activation-log')

    def test_post(self):
        today = datetime.datetime.now(tz=pytz.UTC)

        data = {
            'amount': 200,
            'timestamp': today.strftime('%Y-%m-%dT%H:%M:%S')
        }

        request = self.factory.post(self.url, data=data, format='json')
        force_authenticate(request, self.user)
        response = self.view(request)

        activations = self.circuit.activation_log \
            .order_by('-timestamp') \
            .all()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertActivationLogsEqual([data], activations)

    def test_post_circuit_not_assigned(self):
        today = datetime.datetime.now(tz=pytz.UTC)

        data = {
            'amount': 200,
            'timestamp': today.strftime('%Y-%m-%dT%H:%M:%S')
        }

        self.circuit.controller = None
        self.circuit.save()

        request = self.factory.post(self.url, data=data, format='json')
        force_authenticate(request, self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_unauthenticated(self):
        today = datetime.datetime.now(tz=pytz.UTC)

        data = {
            'amount': 200,
            'timestamp': today.strftime('%Y-%m-%dT%H:%M:%S')
        }

        request = self.factory.post(self.url, data=data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
