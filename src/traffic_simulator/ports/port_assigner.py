import random

from abc import ABC, abstractmethod
from traffic_simulator.models import Flow
from traffic_simulator.ports.port import Port


class PortAssigner(ABC):
    @abstractmethod
    def assign_port(self, flow: Flow) -> Port:
        pass


class UniformPortAssigner(PortAssigner):
    def __init__(self, ports: list[Port]):
        self.ports = ports

    def assign_port(self, flow: Flow) -> Port:
        assigned = random.choice(self.ports)
        flow.assigned_port = assigned.id
        return assigned


class WeightedPortAssigner(PortAssigner):
    def __init__(self, ports: list[Port], weights: list[float]):
        if len(ports) != len(weights):
            raise ValueError("Ports and weights must have the same length.")
        self.ports = ports
        self.weights = weights

    def assign_port(self, flow: Flow) -> Port:
        # random.choices is available in Python 3.6+
        assigned = random.choices(self.ports, weights=self.weights, k=1)[0]
        flow.assigned_port = assigned.id
        return assigned


class InOrderPortAssigner(PortAssigner):
    index: int = 0
    """
    Distributes flows in order equally among links.
    """

    def __init__(self, ports: list[Port]):
        self.ports = ports

    def assign_port(self, flow: Flow) -> Port:
        assigned = self.ports[self.index]
        flow.assigned_port = assigned.id
        self.index = (self.index + 1) % len(self.ports)
        return assigned


class LeastMSEPortAssigner(PortAssigner):
    def __init__(self, ports: list[Port]):
        self.ports = ports

    def assign_port(self, flow: Flow) -> Port:
        # Find the port with the greatest deficit (target utilization - current utilization)
        assigned = max(
            self.ports,
            key=lambda port: max(
                0,
                port.target_utilization
                - port.get_current_utilization(flow.arrival_time),
            ),
        )

        # Assign the flow to the most underutilized port
        flow.assigned_port = assigned.id
        return assigned
