import datetime

import pytz

from smartgarden.models import User, Circuit, Activation, ScheduledOneTimeActivation, ScheduledActivation


def create_user(**kwargs) -> User:
    user = User.objects.create(
        email=kwargs.pop('email', 'user@test.com'),
        username=kwargs.pop('username', 'user'),
        user_type=kwargs.pop('user_type', User.UserType.USER.value)
    )

    password = kwargs.pop('password', 'user')
    user.set_password(password)
    user.save()

    return user


def create_circuit(owner: User, **kwargs) -> Circuit:
    circuit = Circuit.objects.create(
        name=kwargs.pop('name', 'TestCircuit'),
        active=kwargs.pop('active', True),
        health_check=kwargs.pop('active', datetime.datetime.now(tz=pytz.UTC)),
        owner=owner,
        **kwargs
    )

    return circuit


def create_activation(circuit: Circuit, **kwargs) -> Activation:
    activation = Activation.objects.create(
        amount=kwargs.pop('amount', 100),
        timestamp=kwargs.pop('timestamp', datetime.datetime.now(tz=pytz.UTC)),
        circuit=circuit
    )

    return activation


def create_scheduled_one_time_activation(circuit: Circuit, **kwargs) -> ScheduledOneTimeActivation:
    activation = ScheduledOneTimeActivation.objects.create(
        amount=kwargs.pop('amount', 100),
        timestamp=kwargs.pop('timestamp', datetime.datetime.now(tz=pytz.UTC)),
        circuit=circuit
    )

    return activation


def create_scheduled_activation(circuit: Circuit, **kwargs) -> ScheduledActivation:
    activation = ScheduledActivation.objects.create(
        active=kwargs.pop('active', True),
        amount=kwargs.pop('amount', 100),
        time=kwargs.pop('time', datetime.datetime.now(tz=pytz.UTC).time()),
        circuit=circuit
    )

    return activation
