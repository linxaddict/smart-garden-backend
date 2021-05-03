import datetime
from dataclasses import dataclass
from typing import Optional, List

import pytz

from smartgarden.models import ScheduledActivation, ScheduledOneTimeActivation, Circuit


@dataclass
class ScheduledActivationViewModel:
    active: bool
    amount: int
    time: str

    def __init__(self, scheduled_activation: ScheduledActivation) -> None:
        self.active = scheduled_activation.active
        self.amount = scheduled_activation.amount
        self.time = scheduled_activation.time.strftime('%H:%M')


@dataclass
class ScheduledOneTimeActivationViewModel:
    amount: int
    timestamp: str

    def __init__(self, scheduled_activation: ScheduledOneTimeActivation) -> None:
        self.amount = scheduled_activation.amount
        self.timestamp = scheduled_activation.timestamp.strftime('%d-%m-%y %H:%M')


@dataclass
class CircuitViewModel:
    id: int
    name: str
    active: bool
    healthy: bool
    one_time_activation: Optional[ScheduledOneTimeActivationViewModel]
    schedule: List[ScheduledActivationViewModel]

    def __init__(self, circuit: Circuit) -> None:
        self.id = circuit.id
        self.name = circuit.name
        self.active = circuit.active

        if not circuit.health_check:
            self.healthy = False
        else:
            self.healthy = (datetime.datetime.now(tz=pytz.UTC) - circuit.health_check).total_seconds() / 60 < 15

        if not circuit.one_time_activations:
            self.one_time_activation = None
        else:
            one_time_activation = circuit \
                .one_time_activations \
                .filter(timestamp__date=datetime.date.today()) \
                .order_by('-timestamp') \
                .first()

            if not one_time_activation:
                self.one_time_activation = None
            else:
                self.one_time_activation = ScheduledOneTimeActivationViewModel(one_time_activation)

        if not circuit.schedule:
            self.schedule = []
        else:
            self.schedule = [ScheduledActivationViewModel(s) for s in circuit.schedule.order_by('time')]
