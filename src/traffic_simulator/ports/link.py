import collections
from typing import Deque, List

from traffic_simulator.models.flow import Flow


class Link:
    def __init__(self, capacity_bps: float):
        self.capacity_bps = capacity_bps  # Link capacity in bits per second
        self.queue: Deque[Flow] = collections.deque()  # Infinite buffer queue

        self.busy_until: float = 0.0  # Time until current transmission completes
        self.flows: List[Flow] = []

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

        self.queue.append(flow)

        return flow.end_time

    def dequeue_flow(self, current_time: float):
        """
        Remove and return a flow whose transmission is complete.
        Returns None if the flow at the head of the queue has not yet finished.
        """
        if self.queue and current_time >= self.queue[0].end_time:
            flow = self.queue.popleft()
            self.flows.append(flow)

            return flow

        return None

    def _get_remaining_flow_size(self, flow: Flow, current_time: float) -> float:
        """Calculates remaining flow size"""
        if flow.start_time >= current_time:
            return flow.flow_size
        return flow.flow_size - (current_time - flow.start_time) * self.capacity_bps
