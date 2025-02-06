import matplotlib.pyplot as plt

from traffic_simulator.flows.flow_generator import FlowGenerator
from traffic_simulator.ports.port_assigner import PortAssigner
from traffic_simulator.ports.port import Port
from traffic_simulator.ports.port_manager import PortManager


class Simulator:
    def __init__(
        self,
        simulation_time: float,
        flow_generator: FlowGenerator,
        port_manager: PortManager,
        port_ids: list[int],
    ):
        """
        simulation_time: total simulation time.
        time_interval: simulation step (e.g., each second).
        """
        self.simulation_time = simulation_time
        self.flow_generator = flow_generator
        self.all_flows = []
        self.port_manager = port_manager
        self.port_ids = port_ids

    def run(self):
        current_time = 0.0
        flows = self.flow_generator.generate_flows(
            current_time, current_time + self.simulation_time
        )

        # Store data for utilization graph
        time_steps = []
        port_utilizations = {port_id: [] for port_id in self.port_ids}

        for flow in flows:
            # Assign a port to the flow
            self.port_manager.add_flow(flow)
            self.all_flows.append(flow)

            # get utilization data and store it for graph
            time_steps.append(flow.arrival_time)
            for port_id in self.port_ids:
                utilization = self.port_manager.get_port_utilization(port_id, flow.arrival_time)
                port_utilizations[port_id].append(utilization)
        
        # Plot utilization data
        plt.figure(figsize=(10, 6))

        # Plot each port's utilization dynamically
        for port_id, utilization_data in port_utilizations.items():
            plt.plot(time_steps, utilization_data, label=f"Port {port_id} Utilization", marker='o')

        # Add labels and title
        plt.xlabel("Time")
        plt.ylabel("Utilization")
        plt.title("Port Utilization Over Time")
        plt.legend()
        plt.grid(True)

        # Show the plot
        plt.show()

    def visualize_flows_scatter(self):
        arrival_times = [flow.arrival_time for flow in self.all_flows]
        flow_sizes = [flow.flow_size for flow in self.all_flows]

        plt.figure(figsize=(10, 6))
        plt.scatter(arrival_times, flow_sizes)
        plt.xlabel("Arrival Time")
        plt.ylabel("Flow Size")
        plt.title("Flow Arrival Times and Sizes")
        plt.show()
