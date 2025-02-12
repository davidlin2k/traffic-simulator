from dataclasses import dataclass

from traffic_simulator.models.flow import Flow
from traffic_simulator.ports.link import Link


@dataclass
class Event:
    time: float

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        return self.time == other.time


@dataclass
class FlowArrivalEvent(Event):
    flow: Flow


@dataclass
class FlowCompletionEvent(Event):
    flow: Flow
    link: Link
