import collections
from traffic_simulator.models.flow import Flow
from typing import Deque, List, Tuple


class Link:
    def __init__(self, capacity_bps: float):
        self.capacity_bps = capacity_bps  # Link capacity in bits per second
        self.queue: Deque[Flow] = collections.deque()  # Infinite buffer queue

        self.busy_until: float = 0.0  # Time until current transmission completes
        # Instead of cumulative busy time, store busy intervals as tuples (start_time, end_time)
        self.busy_intervals: List[Tuple[float, float]] = []

        # Sampling parameters for recording utilization over time
        self.utilization_samples: List[Tuple[float, float]] = []
        self.last_sample_time: float = 0.0
        self.sample_interval: float = 0.1  # Sample every 100ms

    def enqueue_flow(self, flow: Flow, current_time: float) -> float:
        """
        Enqueue a flow (packet) and schedule its transmission.
        The flow's start and end times are determined based on the link's current busy state.
        Also, record the busy interval.
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
        self.busy_intervals.append((flow.start_time, flow.end_time))
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

    def get_utilization(self, current_time: float, start_time: float = 0.0) -> float:
        """
        Calculate the link utilization (fraction of time busy) over the interval
        from start_time to current_time.
        This is computed by summing the overlaps between the busy intervals and
        the period [start_time, current_time].
        """
        total_busy = 0.0
        interval_length = current_time - start_time

        # Sum the portions of each busy interval that overlap with the sample period.
        for busy_start, busy_end in self.busy_intervals:
            # Find the overlap between [busy_start, busy_end] and [start_time, current_time]
            overlap_start = max(busy_start, start_time)
            overlap_end = min(busy_end, current_time)
            if overlap_start < overlap_end:
                total_busy += overlap_end - overlap_start

        return total_busy / interval_length if interval_length > 0 else 0.0

    def get_utilization(self, current_time: float, start_time: float = 0.0) -> float:
        """
        Calculate the link utilization (fraction of time busy) over the interval
        from start_time to current_time.
        This is computed by summing the overlaps between the busy intervals and
        the period [start_time, current_time].
        """
        total_busy = 0.0
        interval_length = current_time - start_time

        # Sum the portions of each busy interval that overlap with the period.
        for busy_start, busy_end in self.busy_intervals:
            # If the busy interval occurs completely before the start, skip it.
            if busy_end <= start_time:
                continue

            # If the busy interval starts after current_time, we can break out.
            if busy_start >= current_time:
                break

            # Determine the overlapping segment.
            overlap_start = max(busy_start, start_time)
            overlap_end = min(busy_end, current_time)
            if overlap_start < overlap_end:
                total_busy += overlap_end - overlap_start

        return total_busy / interval_length if interval_length > 0 else 0.0

    def get_overall_utilization(self, current_time: float) -> float:
        """
        Calculate the overall link utilization from time 0 up to current_time.
        """
        # Sample utilization at regular intervals
        while self.last_sample_time < current_time:
            utilization = self.get_utilization(self.last_sample_time, 0)
            self.utilization_samples.append((self.last_sample_time, utilization))
            self.last_sample_time += self.sample_interval

        return self.utilization_samples
