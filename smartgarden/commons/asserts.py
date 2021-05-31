from typing import List

from smartgarden.models import Circuit, ScheduledOneTimeActivation, ScheduledActivation, ActivationLog


class CommonAsserts:
    def assertCircuitEqual(self, data: dict, circuit: Circuit) -> None:
        self.assertEqual(data.get('id'), circuit.id)
        self.assertEqual(data.get('name'), circuit.name)
        self.assertEqual(data.get('active'), circuit.active)
        self.assertEqual(data.get('healthy'), circuit.healthy)

        one_time_activation_data = data.get('one_time_activation', None)
        if one_time_activation_data:
            self.assertOneTimeActivationEqual(one_time_activation_data, circuit.one_time_activation)

        scheduled_activations_data = data.get('schedule', [])
        scheduled_activations = circuit.schedule.order_by('-time').all() \
            if circuit.one_time_activations else []

        for ad, a in zip(scheduled_activations_data, scheduled_activations):
            self.assertScheduledActivationEqual(ad, a)

    def assertOneTimeActivationEqual(self, data: dict, activation: ScheduledOneTimeActivation):
        self.assertEqual(data.get('amount'), activation.amount)
        self.assertEqual(data.get('timestamp'), activation.timestamp.strftime('%Y-%m-%dT%H:%M:%S'))

    def assertActivationLogEqual(self, data: dict, activation: ActivationLog):
        self.assertEqual(data.get('amount'), activation.amount)
        self.assertEqual(data.get('timestamp'), activation.timestamp.strftime('%Y-%m-%dT%H:%M:%S'))

    def assertScheduledActivationEqual(self, data: dict, activation: ScheduledActivation):
        self.assertEqual(data.get('active'), activation.active)
        self.assertEqual(data.get('amount'), activation.amount)
        self.assertEqual(data.get('time'), activation.time.strftime('%H:%M:%S'))

    def assertScheduleEqual(self, data: List[dict], schedule: List[ScheduledActivation]):
        for ad, a in zip(data, schedule):
            self.assertScheduledActivationEqual(ad, a)

    def assertOneTimeActivationsEqual(self, data: List[dict], activations: List[ScheduledOneTimeActivation]):
        for ad, a in zip(data, activations):
            self.assertOneTimeActivationEqual(ad, a)

    def assertActivationLogsEqual(self, data: List[dict], activations: List[ActivationLog]):
        for ad, a in zip(data, activations):
            self.assertActivationLogEqual(ad, a)
