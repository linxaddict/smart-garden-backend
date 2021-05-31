import datetime

import pytz
from django.core.management import BaseCommand, call_command

from smartgarden.models import User, Circuit, ActivationLog, ScheduledOneTimeActivation, ScheduledActivation


class Command(BaseCommand):
    def create_user(self, **kwargs) -> User:
        user = User.objects.create(
            email=kwargs.pop('email', 'user@test.com'),
            username=kwargs.pop('username', 'user'),
            user_type=kwargs.pop('user_type', User.UserType.USER.value)
        )

        password = kwargs.pop('password', 'user')
        user.set_password(password)
        user.save()

        self.stdout.write(f"Test user account created: [{user.email}, {password}]")

        return user

    def create_circuit(self, owner: User, **kwargs) -> Circuit:
        circuit = Circuit.objects.create(
            name=kwargs.pop('name', 'TestCircuit'),
            active=kwargs.pop('active', True),
            health_check=kwargs.pop('active', datetime.datetime.now(tz=pytz.UTC)),
            owner=owner
        )

        self.stdout.write(f"Test circuit created: [{circuit.name}]")

        return circuit

    def create_activation(self, circuit: Circuit, **kwargs) -> ActivationLog:
        activation = ActivationLog.objects.create(
            amount=kwargs.pop('amount', 100),
            timestamp=kwargs.pop('timestamp', datetime.datetime.now(tz=pytz.UTC)),
            circuit=circuit
        )

        self.stdout.write(f"Test activation created: [{activation.amount}, {activation.timestamp}]")

        return activation

    def create_scheduled_one_time_activation(self, circuit: Circuit, **kwargs) -> ScheduledOneTimeActivation:
        activation = ScheduledOneTimeActivation.objects.create(
            amount=kwargs.pop('amount', 100),
            timestamp=kwargs.pop('timestamp', datetime.datetime.now(tz=pytz.UTC)),
            circuit=circuit
        )

        self.stdout.write(f"Test one-time activation created: [{activation.amount}, {activation.timestamp}]")

        return activation

    def create_scheduled_activation(self, circuit: Circuit, **kwargs) -> ScheduledActivation:
        activation = ScheduledActivation.objects.create(
            active=kwargs.pop('active', True),
            amount=kwargs.pop('amount', 100),
            time=kwargs.pop('time', datetime.datetime.now(tz=pytz.UTC).time()),
            circuit=circuit
        )

        self.stdout.write(f"Test scheduled activation created: [{activation.amount}, {activation.time}]")

        return activation

    def handle(self, *args, **options):
        call_command('flush', interactive=False)

        user = self.create_user()
        circuit_1 = self.create_circuit(owner=user)

        self.create_activation(circuit=circuit_1)
        self.create_scheduled_one_time_activation(circuit=circuit_1)
        self.create_scheduled_activation(circuit=circuit_1)
        self.create_scheduled_activation(circuit=circuit_1, amount=150)
        self.create_scheduled_activation(circuit=circuit_1, amount=200, active=False)

        circuit_2 = self.create_circuit(owner=user, name='TestCircuit_2')

        self.create_activation(circuit=circuit_2)
        self.create_scheduled_one_time_activation(circuit=circuit_2)
        self.create_scheduled_activation(circuit=circuit_2)
        self.create_scheduled_activation(circuit=circuit_2, amount=200)
        self.create_scheduled_activation(circuit=circuit_2, amount=200)

        self.create_user(
            email='admin@test.com',
            password='admin',
            username='admin',
            user_type=User.UserType.ADMIN.value
        )
