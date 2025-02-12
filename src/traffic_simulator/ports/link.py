import collections
from typing import Deque, List, Tuple

from traffic_simulator.models.flow import Flow
from traffic_simulator.models.link_metrics import LinkMetrics

class Link:
    LINK_UTILIZATION = "Link Utilization"
    BUFFER_OCCUPANCY = "Buffer Occupancy"

    def __init__(self, capacity_bps: float):
        self.capacity_bps = capacity_bps  # Link capacity in bits per second
        self.queue: Deque[Flow] = collections.deque()  # Infinite buffer queue

        self.busy_until: float = 0.0  # Time until current transmission completes
        self.flows: List[Flow] = []

        self.metrics = LinkMetrics()

    def enqueue_flow(self, flow: Flow, current_time: float) -> float:
        """
        Enqueue a flow (packet) and schedule its transmission.
        The flow's start and end times are determined based on the link's current busy state.
        Also, record the flow to get the stats at end of simulation.
        Returns the scheduled end_time (i.e. when transmission completes).
        """
        transmission_time = flow.flow_size / self.capacity_bps

        if not self.queue and current_time >= self.busy_until:
            # Link is idle; transmit immediately.
            flow.start_time = current_time
            flow.end_time = current_time + transmission_time
        else:
            # Link is busy; schedule after current busy period.
            flow.start_time = self.busy_until
            flow.end_time = self.busy_until + transmission_time

        # Update the link's busy state and record the busy interval.
        self.busy_until = flow.end_time

        self.flows.append(flow)
        self.queue.append(flow)

        return flow.end_time

    def dequeue_flow(self, current_time: float):
        """
        Remove and return a flow whose transmission is complete.
        Returns None if the flow at the head of the queue has not yet finished.
        """
        if self.queue and current_time >= self.queue[0].end_time:
            return self.queue.popleft()
        return None

    def _get_remaining_flow_size(self, flow: Flow, current_time: float) -> float:
        """Calculates remaining flow size"""
        if flow.start_time >= current_time:
            return flow.flow_size
        return flow.flow_size - (current_time - flow.start_time) * self.capacity_bps

    def _calculate_buffer_occupancy(self, current_time: float) -> float:
        """Calculates current buffer occupancy"""
        return sum(
            self._get_remaining_flow_size(flow, current_time)
            for flow in self.queue
            if flow.end_time > current_time
        )

    def _calculate_utilization(self, current_time: float, start_time: float = 0.0) -> float:
        """Calculates link utilization"""
        if start_time >= current_time:
            return 0.0

        total_busy = sum(
            min(flow.end_time, current_time) - max(flow.start_time, start_time)
            for flow in self.flows
            if flow.end_time > start_time and flow.start_time < current_time
        )
        
        return total_busy / (current_time - start_time)
    
    def get_current_metrics(self, current_time: float) -> dict[str, float]:
        """Returns current link metrics"""
        return {
            self.LINK_UTILIZATION: self._calculate_utilization(current_time),
            self.BUFFER_OCCUPANCY: self._calculate_buffer_occupancy(current_time)
        }
    
    def sample_metrics(self, current_time: float) -> None:
        """Samples and stores metrics at regular intervals"""
        while self.metrics.last_sample_time < current_time:
            current_metrics = self.get_current_metrics(self.metrics.last_sample_time)
            
            self.metrics.utilization_samples.append(
                (self.metrics.last_sample_time, current_metrics[self.LINK_UTILIZATION])
            )
            self.metrics.buffer_occupancy_samples.append(
                (self.metrics.last_sample_time, current_metrics[self.BUFFER_OCCUPANCY])
            )
            
            self.metrics.last_sample_time += self.metrics.sample_interval
