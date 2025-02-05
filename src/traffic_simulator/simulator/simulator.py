import matplotlib.pyplot as plt

from traffic_simulator.flows.flow_generator import FlowGenerator
from traffic_simulator.metrics.utilization import calculate_link_utilization_multiple
from traffic_simulator.ports.port_assigner import PortAssigner


class Simulator:
    def __init__(
        self,
        simulation_time: float,
        flow_generator: FlowGenerator,
        port_assigner: PortAssigner,
        link_capacities: dict[int, float],
    ):
        """
        simulation_time: total simulation time.
        time_interval: simulation step (e.g., each second).
        """
        self.simulation_time = simulation_time
        self.flow_generator = flow_generator
        self.port_assigner = port_assigner
        self.link_capacities = link_capacities
        self.all_flows = []

    def run(self):
        current_time = 0.0
        flows = self.flow_generator.generate_flows(
            current_time, current_time + self.simulation_time
        )

        for flow in flows:
            # Assign a port to the flow
            self.port_assigner.assign_port(flow)
            self.all_flows.append(flow)

    def print_statistics(self):
        print(f"Total flows generated: {len(self.all_flows)}")
        link_utilization = calculate_link_utilization_multiple(
            self.all_flows, self.link_capacities, self.simulation_time
        )
        print("Link Utilization:")
        for link, util in link_utilization.items():
            print(
                f"  Link {link}: {util * 100:.2f}% (Capacity: {self.link_capacities[link]} bps)"
            )

    def visualize_flows_scatter(self):
        arrival_times = [flow.arrival_time for flow in self.all_flows]
        flow_sizes = [flow.flow_size for flow in self.all_flows]

        plt.figure(figsize=(10, 6))
        plt.scatter(arrival_times, flow_sizes)
        plt.xlabel("Arrival Time")
        plt.ylabel("Flow Size")
        plt.title("Flow Arrival Times and Sizes")
        plt.show()
