import random

from abc import ABC, abstractmethod
from traffic_simulator.models import Flow


class PortAssigner(ABC):
    @abstractmethod
    def assign_port(self, flow: Flow) -> int:
        pass


class UniformPortAssigner(PortAssigner):
    def __init__(self, ports: list[int]):
        self.ports = ports

    def assign_port(self, flow: Flow) -> int:
        assigned = random.randrange(len(self.ports))
        flow.assigned_port = assigned
        return assigned


class WeightedPortAssigner(PortAssigner):
    def __init__(self, ports: list[int], weights: list[float]):
        if len(ports) != len(weights):
            raise ValueError("Ports and weights must have the same length.")
        self.ports = ports
        self.weights = weights

    def assign_port(self, flow: Flow) -> int:
        # random.choices is available in Python 3.6+
        assigned = random.choices(self.ports, weights=self.weights, k=1)[0]
        flow.assigned_port = assigned
        return assigned
