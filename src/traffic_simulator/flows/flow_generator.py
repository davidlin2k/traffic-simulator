import random

from abc import ABC, abstractmethod
from typing import Iterator
from traffic_simulator.flows.flow_size_generator import FlowSizeGenerator
from traffic_simulator.models import Flow


class FlowGenerator(ABC):
    def __init__(self, flow_size_generator: FlowSizeGenerator):
        self.flow_size_generator = flow_size_generator
        self.all_flows: list[Flow] = []

    @abstractmethod
    def generate_flows(self, current_time: float, end_time: float) -> Iterator[Flow]:
        pass


class PoissonFlowGenerator(FlowGenerator):
    """
    Generates flows using a Poisson process for arrivals.
    """

    def __init__(self, arrival_rate: float, flow_size_generator: FlowSizeGenerator):
        """
        arrival_rate: Expected number of flows per time interval (λ).
        flow_size_generator: An instance of FlowSizeGenerator.
        """
        super().__init__(flow_size_generator)
        self.arrival_rate = arrival_rate
        self.next_flow_id = 0

    def generate_flows(self, current_time: float, end_time: float) -> Iterator[Flow]:
        while current_time < end_time:
            flow_size = self.flow_size_generator.generate()
            current_time += random.expovariate(self.arrival_rate)

            flow = Flow(
                id=self.next_flow_id, arrival_time=current_time, flow_size=flow_size
            )
            self.all_flows.append(flow)
            self.next_flow_id += 1

            yield flow
