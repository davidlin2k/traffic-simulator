from pathlib import Path
import matplotlib.pyplot as plt
import heapq
import numpy as np

from traffic_simulator.flows.flow_generator import FlowGenerator, FlowSizeGenerator
from traffic_simulator.metrics.metric_manager import LinkMetricsTracker
from traffic_simulator.ports.link import Link
from traffic_simulator.ports.strategy import LoadBalanceStrategy
from traffic_simulator.models.event import (
    Event,
    FlowArrivalEvent,
    FlowCompletionEvent,
)
from traffic_simulator.simulator.visualizer import LinkVisualizer
from typing import List
from traffic_simulator.config.models import LinkConfig
from traffic_simulator.metrics.mse import calculate_mse, calculate_per_link_errors

import logging


class Simulator:
    def __init__(
        self,
        duration: float,
        flow_generator: FlowGenerator,
        flow_size_generator: FlowSizeGenerator,
        strategy: LoadBalanceStrategy,
        links: list[Link],
        link_configs: List[LinkConfig],
        link_metric_tracker: LinkMetricsTracker,
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
        self.link_configs = link_configs

        # Initialize MSE tracking
        self.mse_samples = []
        self.mse_timestamps = []
        self.sample_interval = 1.0

        # To graph flow size
        self.flow_size_generator = flow_size_generator

        # Initialize simulation state
        self._time = 0.0
        self._events: list[Event] = []

        self.metrics_tracker = link_metric_tracker
        self.visualizer = LinkVisualizer(self.metrics_tracker)

    def _sample_mse(self):
        """Sample and store current MSE value"""
        mse = calculate_mse(
            self.metrics_tracker, self.links, self.link_configs, self._time
        )
        self.mse_samples.append(mse)
        self.mse_timestamps.append(self._time)

    def run(self):
        # Generate initial events
        self._generate_flow_events()

        while self._events:
            # Get the next event
            event = heapq.heappop(self._events)
            self._time = event.time

            self._sample_stats()

            if isinstance(event, FlowArrivalEvent):
                self._process_packet_arrival(event)
            elif isinstance(event, FlowCompletionEvent):
                self._process_packet_completion(event)

            # Log progress
            print(f"time: {self._time:.2f}, event_type: {event.__class__.__name__}")

        self._sample_stats()
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
        link = self.strategy.select_link(event)

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

    def _sample_stats(self):
        # Sample link utilizations and buffer occupancy
        self.metrics_tracker.sample_metrics(self._time)
        self._sample_mse()

    def visualize(self, save_path: str = None):
        self.visualizer.plot_utilization(self.links, save_path=save_path)
        self.visualizer.plot_max_utilization(self.links, save_path=save_path)
        self.visualizer.plot_variance(self.links, save_path=save_path)
        self.visualizer.plot_buffer_occupancy(self.links, save_path=save_path)
        self.visualizer.plot_fct(self.links, save_path=save_path)

        self._visualize_flows_scatter(save_path)

        # Add MSE visualization
        self._visualize_mse(save_path)

        # Add per-link error visualization
        self._visualize_per_link_errors(save_path)

        self._visualize_workload_sizes(save_path)

    def _visualize_workload_sizes(self, save_path):
        """Plots the cumulative probability distribution using the quantile function with a logarithmic x-axis."""
        probabilities = np.linspace(0.00, 1.00, 100)  # 100 samples from 0.00 to 1.00
        flow_sizes = [self.flow_size_generator.generate_with_probability(p) for p in probabilities]

        # Plot the CDF
        plt.figure(figsize=(8, 5))
        plt.plot(flow_sizes, probabilities, marker='o', linestyle='-', color='b', markersize=3, 
                label="CDF (Each point is 1% probability equally spaced apart)")
        
        plt.xlabel("Flow Size")
        plt.ylabel("Cumulative Probability")
        plt.title("Cumulative Distribution Function (Log-Scale X)")
        
        plt.xscale("log")  # Set the x-axis to log scale
        plt.xticks([10**i for i in range(1, int(np.log10(max(flow_sizes))) + 1)])  # Log-spaced ticks

        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.legend()

        if save_path:
            plt.savefig(Path(save_path) / "flow_size_cumulative_probability.png", bbox_inches="tight", dpi=300)

    def _visualize_mse(self, save_path: str = None):
        """Plot MSE over time"""
        plt.figure(figsize=(10, 6))
        plt.plot(self.mse_timestamps, self.mse_samples)
        plt.xlabel("Time (seconds)")
        plt.ylabel("Mean Square Error")
        plt.title("Link Utilization Mean Square Error Over Time")
        plt.grid(True)

        if save_path:
            plt.savefig(Path(save_path) / "mse.png", bbox_inches="tight", dpi=300)

    def _visualize_per_link_errors(self, save_path: str = None):
        """Plot squared errors for each link"""
        final_errors = calculate_per_link_errors(
            self.metrics_tracker, self.links, self.link_configs, self._time
        )

        plt.figure(figsize=(10, 6))
        links = list(final_errors.keys())
        errors = list(final_errors.values())

        plt.bar(links, errors)
        plt.xlabel("Link ID")
        plt.ylabel("Squared Error")
        plt.title("Final Squared Error per Link")

        if save_path:
            plt.savefig(
                Path(save_path) / "per_link_errors.png", bbox_inches="tight", dpi=300
            )

    def _visualize_flows_scatter(self, save_path: str = None):
        arrival_times = [flow.arrival_time for flow in self.flow_generator.all_flows]
        flow_sizes = [flow.flow_size for flow in self.flow_generator.all_flows]

        plt.figure(figsize=(10, 6))
        plt.scatter(arrival_times, flow_sizes)
        plt.xlabel("Arrival Time")
        plt.ylabel("Flow Size")
        plt.title("Flow Arrival Times and Sizes")

        if save_path:
            plt.savefig(
                Path(save_path) / "flows_scatter.png", bbox_inches="tight", dpi=300
            )
