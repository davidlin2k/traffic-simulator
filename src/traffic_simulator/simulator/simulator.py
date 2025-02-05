import matplotlib.pyplot as plt

from traffic_simulator.flows.flow_generator import FlowGenerator
from traffic_simulator.models.flow import Flow


class Simulator:
    def __init__(
        self,
        simulation_time: float,
        flow_generator: FlowGenerator,
    ):
        """
        simulation_time: total simulation time.
        time_interval: simulation step (e.g., each second).
        """
        self.simulation_time = simulation_time
        self.flow_generator = flow_generator
        self.all_flows: list[Flow] = []

    def run(self):
        current_time = 0.0
        flows = self.flow_generator.generate_flows(
            current_time, current_time + self.simulation_time
        )
        self.all_flows.extend(flows)

    def print_statistics(self):
        print(f"Total flows generated: {len(self.all_flows)}")
        print(f"Flows: {self.all_flows}")

    def visualize_flows_scatter(self):
        arrival_times = [flow.arrival_time for flow in self.all_flows]
        flow_sizes = [flow.flow_size for flow in self.all_flows]

        plt.figure(figsize=(10, 6))
        plt.scatter(arrival_times, flow_sizes)
        plt.xlabel("Arrival Time")
        plt.ylabel("Flow Size")
        plt.title("Flow Arrival Times and Sizes")
        plt.show()
