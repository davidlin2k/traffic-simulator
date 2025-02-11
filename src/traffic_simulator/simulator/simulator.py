from pathlib import Path
import matplotlib.pyplot as plt
import heapq

from traffic_simulator.flows.flow_generator import FlowGenerator
from traffic_simulator.ports.link import Link
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

    def visualize(self, save_path: str = None):
        link_visualizer = LinkVisualizer()
        link_visualizer.plot_utilization(self.links, save_path=save_path)

        self._visualize_flows_scatter(save_path)
        
    def _visualize_flows_scatter(self, save_path: str = None):
        arrival_times = [flow.arrival_time for flow in self.flow_generator.all_flows]
        flow_sizes = [flow.flow_size for flow in self.flow_generator.all_flows]

        plt.figure(figsize=(10, 6))
        plt.scatter(arrival_times, flow_sizes)
        plt.xlabel("Arrival Time")
        plt.ylabel("Flow Size")
        plt.title("Flow Arrival Times and Sizes")

        if save_path:
            plt.savefig(Path(save_path) / "flows_scatter.png", bbox_inches="tight", dpi=300)
        