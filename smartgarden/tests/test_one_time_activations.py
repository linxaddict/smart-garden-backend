import datetime

import pytz
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from smartgarden.commons.asserts import CommonAsserts
from smartgarden.commons.fixtures import create_user, create_circuit, create_scheduled_one_time_activation
from smartgarden.views import CircuitOneTimeActivationView


class CircuitOneTimeActivationViewTest(APITestCase, CommonAsserts):
    def setUp(self):
        self.user = create_user()
        self.circuit = create_circuit(name='c1')
        self.circuit.collaborators.add(self.user)

        self.view = CircuitOneTimeActivationView.as_view()
        self.factory = APIRequestFactory()
        self.url = reverse('circuit-one-time-activations', kwargs={'circuit_id': self.circuit.pk})

    def test_fetch(self):
        today = datetime.datetime.now(tz=pytz.UTC)
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - + datetime.timedelta(days=1)

        create_scheduled_one_time_activation(self.circuit, timestamp=yesterday)
        s2 = create_scheduled_one_time_activation(self.circuit, timestamp=today)
        create_scheduled_one_time_activation(self.circuit, timestamp=tomorrow)

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertOneTimeActivationsEqual(response.data, [s2])

    def test_fetch_no_activations(self):
        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, [])

    def test_fetch_unauthenticated(self):
        request = self.factory.get(self.url, format='json')
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fetch_circuit_not_related(self):
        today = datetime.datetime.now(tz=pytz.UTC)
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - + datetime.timedelta(days=1)

        create_scheduled_one_time_activation(self.circuit, timestamp=yesterday)
        s2 = create_scheduled_one_time_activation(self.circuit, timestamp=today)
        create_scheduled_one_time_activation(self.circuit, timestamp=tomorrow)

        user2 = create_user(email="user2@test.com")

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, user2)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertOneTimeActivationsEqual(response.data, [s2])

    def test_fetch_as_collaborators(self):
        today = datetime.datetime.now(tz=pytz.UTC)
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - + datetime.timedelta(days=1)

        create_scheduled_one_time_activation(self.circuit, timestamp=yesterday)
        s2 = create_scheduled_one_time_activation(self.circuit, timestamp=today)
        create_scheduled_one_time_activation(self.circuit, timestamp=tomorrow)

        user2 = create_user(email="user2@test.com")
        self.circuit.collaborators.add(user2)

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, user2)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertOneTimeActivationsEqual(response.data, [s2])

    def test_post(self):
        today = datetime.datetime.now(tz=pytz.UTC)

        data = {
            'amount': 200,
            'timestamp': today.strftime('%Y-%m-%dT%H:%M:%S')
        }

        request = self.factory.post(self.url, data=data, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, circuit_id=self.circuit.pk)

        activation = self.circuit.one_time_activations \
            .filter(timestamp__date=datetime.date.today()) \
            .order_by('-timestamp') \
            .first()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertOneTimeActivationEqual(data, activation)

    def test_post_circuit_not_owned(self):
        today = datetime.datetime.now(tz=pytz.UTC)

        data = {
            'amount': 200,
            'timestamp': today.strftime('%Y-%m-%dT%H:%M:%S')
        }

        user2 = create_user(email="user2@test.com")

        request = self.factory.post(self.url, data=data, format='json')
        force_authenticate(request, user2)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_as_collaborator(self):
        today = datetime.datetime.now(tz=pytz.UTC)

        data = {
            'amount': 200,
            'timestamp': today.strftime('%Y-%m-%dT%H:%M:%S')
        }

        user2 = create_user(email="user2@test.com")
        self.circuit.collaborators.add(user2)

        request = self.factory.post(self.url, data=data, format='json')
        force_authenticate(request, user2)
        response = self.view(request, circuit_id=self.circuit.pk)

        activation = self.circuit.one_time_activations \
            .filter(timestamp__date=datetime.date.today()) \
            .order_by('-timestamp') \
            .first()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertOneTimeActivationEqual(data, activation)

    def test_post_unauthenticated(self):
        today = datetime.datetime.now(tz=pytz.UTC)

        data = {
            'amount': 200,
            'timestamp': today.strftime('%Y-%m-%dT%H:%M:%S')
        }

        request = self.factory.post(self.url, data=data, format='json')
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
