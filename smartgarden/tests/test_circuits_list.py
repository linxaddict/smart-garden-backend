import datetime

import pytz
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from smartgarden.commons.asserts import CommonAsserts
from smartgarden.commons.fixtures import create_user, create_circuit, create_scheduled_one_time_activation, \
    create_scheduled_activation
from smartgarden.views import CircuitViewSet


class CircuitViewSetTest(APITestCase, CommonAsserts):
    def setUp(self):
        self.user = create_user()
        self.view = CircuitViewSet.as_view(actions={
            'get': 'list'
        })
        self.factory = APIRequestFactory()
        self.url = reverse('circuit-list')

    def test_fetch_many_circuits_unauthenticated(self):
        request = self.factory.get(self.url, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch_many_circuits(self):
        c1 = create_circuit(name='c1')
        c1.collaborators.add(self.user)
        c2 = create_circuit(name='c2')
        c2.collaborators.add(self.user)
        create_circuit(name='c3')

        create_scheduled_one_time_activation(c1)
        create_scheduled_one_time_activation(c1)

        create_scheduled_activation(c1)
        create_scheduled_activation(c1)

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(2, len(response.data))
        self.assertCircuitEqual(response.data[0], c1)
        self.assertCircuitEqual(response.data[1], c2)

    def test_fetch_many_circuits_no_related(self):
        c1 = create_circuit(name='c1')
        create_circuit(name='c2')
        create_circuit(name='c3')

        create_scheduled_one_time_activation(c1)
        create_scheduled_one_time_activation(c1)

        create_scheduled_activation(c1)
        create_scheduled_activation(c1)

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))

    def test_fetch_many_circuits_no_activations_no_schedule(self):
        c1 = create_circuit(name='c1')
        c1.collaborators.add(self.user)
        c2 = create_circuit(name='c2')
        c2.collaborators.add(self.user)
        create_circuit(name='c3')

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(2, len(response.data))
        self.assertIsNone(response.data[0].get('one_time_activation'))
        self.assertListEqual([], response.data[0].get('schedule'))
        self.assertIsNone(response.data[1].get('one_time_activation'))
        self.assertListEqual([], response.data[1].get('schedule'))

        self.assertCircuitEqual(response.data[0], c1)
        self.assertCircuitEqual(response.data[1], c2)

    def test_fetch_many_circuits_activations_not_for_today(self):
        c1 = create_circuit(name='c1')
        c1.collaborators.add(self.user)
        c2 = create_circuit(name='c2')
        c2.collaborators.add(self.user)
        create_circuit(name='c3')

        today = datetime.datetime.now(tz=pytz.UTC)
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - + datetime.timedelta(days=1)

        create_scheduled_one_time_activation(c1, timestamp=tomorrow)
        create_scheduled_one_time_activation(c1, timestamp=yesterday)

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(2, len(response.data))
        self.assertIsNone(response.data[0].get('one_time_activation'))
        self.assertListEqual([], response.data[0].get('schedule'))
        self.assertIsNone(response.data[1].get('one_time_activation'))
        self.assertListEqual([], response.data[1].get('schedule'))

        self.assertCircuitEqual(response.data[0], c1)
        self.assertCircuitEqual(response.data[1], c2)
