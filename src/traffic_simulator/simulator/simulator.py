import matplotlib.pyplot as plt
import heapq

from traffic_simulator.flows.flow_generator import FlowGenerator
from traffic_simulator.ports.link import Link
from traffic_simulator.ports.port_manager import PortManager
from pathlib import Path
from traffic_simulator.ports.strategy import LoadBalanceStrategy
from traffic_simulator.simulator.event import (
    Event,
    FlowArrivalEvent,
    FlowCompletionEvent,
)
from traffic_simulator.simulator.visualizer import LinkVisualizer


class Simulator:
    def __init__(
        self,
        duration: float,
        flow_generator: FlowGenerator,
        strategy: LoadBalanceStrategy,
        links: list[Link],
        config_file: str,
    ):
        """
        duration: total simulation time.
        time_interval: simulation step (e.g., each second).
        """
        # Initialize simulation components
        self.duration = duration
        self.flow_generator = flow_generator
        self.strategy = strategy
        self.links = links

        # Initialize simulation state
        self._time = 0.0
        self._events: list[Event] = []

        # Create graphs directory if it doesn't exist
        self.graphs_dir = Path("graphs")
        self.graphs_dir.mkdir(exist_ok=True)

        # Extract base name from config file for graph naming
        config_base = Path(config_file).stem  # Gets filename without extension
        self.graph_prefix = f"graph_{config_base}"


    def run(self):
        # Generate initial events
        self._generate_flow_events()

        while self._events:
            # Get the next event
            event = heapq.heappop(self._events)
            self._time = event.time

            if isinstance(event, FlowArrivalEvent):
                self._process_packet_arrival(event)
            elif isinstance(event, FlowCompletionEvent):
                self._process_packet_completion(event)

        self._sample_link_utilizations()
        self.visualize()
        self._visualize_flows_scatter()

    def _generate_flow_events(self):
        # Generate flow arrival events
        for flow in self.flow_generator.generate_flows(0, self.duration):
            arrival_event = FlowArrivalEvent(
                time=flow.arrival_time,
                flow=flow,
            )
            heapq.heappush(self._events, arrival_event)

    def _process_packet_arrival(self, event: FlowArrivalEvent):
        """Handle packet arrival event"""
        link = self.strategy.select_link()

        # Schedule packet transmission completion
        finish_time = link.enqueue_flow(event.flow, self._time)
        completion_event = FlowCompletionEvent(
            time=finish_time,
            flow=event.flow,
            link=link,
        )
        heapq.heappush(self._events, completion_event)

    def _process_packet_completion(self, event: FlowCompletionEvent):
        """Handle packet completion event"""
        link = event.link
        link.dequeue_flow(self._time)

    def _sample_link_utilizations(self):
        # Sample link utilizations
        for link in self.links:
            link.get_overall_utilization(self._time)

    def visualize(self):
        visualizer = LinkVisualizer()
        visualizer.plot_utilization(self.links)

    def _visualize_port_utilization(self, time_steps, port_utilizations):
        # Plot utilization data
        plt.figure(figsize=(10, 6))

        # Plot each port's utilization dynamically
        for port_id, utilization_data in port_utilizations.items():
            plt.plot(
                time_steps,
                utilization_data,
                label=f"Port {port_id} Utilization",
                marker="o",
            )

        # Add labels and title
        plt.xlabel("Time")
        plt.ylabel("Utilization")
        plt.title("Port Utilization Over Time")
        plt.legend()
        plt.grid(True)

        # Save the plot to the graph folder (utilization plot)
        filename = self.graphs_dir / f"{self.graph_prefix}_utilization.png"
        plt.savefig(filename)
        plt.close()
        print(f"Saved port utilization graph to {filename}")

        # Generate and save other visualizations
        self.visualize_flows_scatter()


    def _visualize_flows_scatter(self):
        arrival_times = [flow.arrival_time for flow in self.flow_generator.all_flows]
        flow_sizes = [flow.flow_size for flow in self.flow_generator.all_flows]

        plt.figure(figsize=(10, 6))
        plt.scatter(arrival_times, flow_sizes)
        plt.xlabel("Arrival Time")
        plt.ylabel("Flow Size")
        plt.title("Flow Arrival Times and Sizes")

       # Save the plot to the graph folder (scatter plot)
        filename = self.graphs_dir / f"{self.graph_prefix}_scatter.png"
        plt.savefig(filename)
        plt.close()
        print(f"Saved flow scatter plot to {filename}")