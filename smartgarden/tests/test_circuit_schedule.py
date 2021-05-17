import datetime

import pytz
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from smartgarden.commons.asserts import CommonAsserts
from smartgarden.commons.fixtures import create_user, create_circuit, create_scheduled_activation
from smartgarden.views import CircuitScheduleView


class CircuitScheduleViewTest(APITestCase, CommonAsserts):
    def setUp(self):
        self.user = create_user()
        self.circuit = create_circuit(owner=self.user, name='c1')

        self.view = CircuitScheduleView.as_view()
        self.factory = APIRequestFactory()
        self.url = reverse('circuit-schedule', kwargs={'circuit_id': self.circuit.pk})

    def test_fetch_unauthenticated(self):
        request = self.factory.get(self.url, format='json')
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fetch(self):
        today = datetime.datetime.now(tz=pytz.UTC)
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - + datetime.timedelta(days=1)

        s1 = create_scheduled_activation(self.circuit, timestamp=yesterday)
        s2 = create_scheduled_activation(self.circuit, timestamp=today)
        s3 = create_scheduled_activation(self.circuit, timestamp=tomorrow)

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertScheduleEqual(response.data, [s1, s2, s3])

    def test_fetch_no_schedule(self):
        request = self.factory.get(self.url, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, [])

    def test_fetch_circuit_not_owned(self):
        today = datetime.datetime.now(tz=pytz.UTC)
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - + datetime.timedelta(days=1)

        s1 = create_scheduled_activation(self.circuit, timestamp=yesterday)
        s2 = create_scheduled_activation(self.circuit, timestamp=today)
        s3 = create_scheduled_activation(self.circuit, timestamp=tomorrow)

        user2 = create_user(email="user2@test.com")

        request = self.factory.get(self.url, format='json')
        force_authenticate(request, user2)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertScheduleEqual(response.data, [s1, s2, s3])

    def test_put(self):
        today = datetime.datetime.now(tz=pytz.UTC)
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - + datetime.timedelta(days=1)

        create_scheduled_activation(self.circuit, timestamp=yesterday)
        create_scheduled_activation(self.circuit, timestamp=today)
        create_scheduled_activation(self.circuit, timestamp=tomorrow)

        data = [
            {
                'active': False,
                'amount': 200,
                'time': '21:00:49'
            }
        ]

        request = self.factory.put(self.url, data=data, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertScheduleEqual(data, self.circuit.schedule.all())

    def test_put_initial_schedule_empty(self):
        data = [
            {
                'active': False,
                'amount': 200,
                'time': '21:00:49'
            }
        ]

        request = self.factory.put(self.url, data=data, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertScheduleEqual(data, self.circuit.schedule.all())

    def test_put_clear_schedule(self):
        today = datetime.datetime.now(tz=pytz.UTC)
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - + datetime.timedelta(days=1)

        create_scheduled_activation(self.circuit, timestamp=yesterday)
        create_scheduled_activation(self.circuit, timestamp=today)
        create_scheduled_activation(self.circuit, timestamp=tomorrow)

        data = []

        request = self.factory.put(self.url, data=data, format='json')
        force_authenticate(request, self.user)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertScheduleEqual(data, self.circuit.schedule.all())

    def test_put_unauthenticated(self):
        data = [
            {
                'active': False,
                'amount': 200,
                'time': '21:00:49'
            }
        ]

        request = self.factory.put(self.url, data=data, format='json')
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_circuit_not_owned(self):
        today = datetime.datetime.now(tz=pytz.UTC)
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - + datetime.timedelta(days=1)

        create_scheduled_activation(self.circuit, timestamp=yesterday)
        create_scheduled_activation(self.circuit, timestamp=today)
        create_scheduled_activation(self.circuit, timestamp=tomorrow)

        data = [
            {
                'active': False,
                'amount': 200,
                'time': '21:00:49'
            }
        ]

        user2 = create_user(email="user2@test.com")

        request = self.factory.put(self.url, data=data, format='json')
        force_authenticate(request, user2)
        response = self.view(request, circuit_id=self.circuit.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
