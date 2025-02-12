import collections
from traffic_simulator.models.flow import Flow
from typing import Deque, List, Tuple


class Link:
    LINK_UTILIZATION = "Link Utilization"
    BUFFER_OCCUPANCY = "Buffer Occupancy"

    def __init__(self, capacity_bps: float):
        self.capacity_bps = capacity_bps  # Link capacity in bits per second
        self.queue: Deque[Flow] = collections.deque()  # Infinite buffer queue

        self.busy_until: float = 0.0  # Time until current transmission completes
        self.flows: List[Flow] = []

        # Sampling parameters for recording stats (utilization and buffer occupancy) over time

        self.stats_keys = {
            self.LINK_UTILIZATION : "utilization_samples", 
            self.BUFFER_OCCUPANCY : "buffer_occupancy_samples"
        }

        self.utilization_samples: List[Tuple[float, float]] = []
        self.buffer_occupancy_samples: List[Tuple[float, float]] = []

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

    def get_stats(self, current_time: float, start_time: float = 0.0) -> dict[str, float]:
        """
        Calculate the link utilization (fraction of time busy) over the interval
        from start_time to current_time.
        This is computed by summing the overlaps between the busy intervals and
        the period [start_time, current_time].
        """
        if start_time >= current_time:
            return {key: 0.0 for key, _ in self.stats_keys.items()}

        total_busy = 0.0
        buffer_occupancy = 0.0
        interval_length = current_time - start_time

        # Sum the portions of each busy interval that overlap with the period.
        for flow in self.flows:
            busy_start = flow.start_time
            busy_end = flow.end_time
            arrival = flow.arrival_time
            
            # If the busy interval occurs completely before the start, skip it.
            if busy_end <= start_time:
                continue

            # If the flow arrived after current time, we can break out.
            if arrival >= current_time:
                break

            # Only add to total_busy if the busy interval starts before current_time.
            if busy_start < current_time:
                # Determine the overlapping segment.
                overlap_start = max(busy_start, start_time)
                overlap_end = min(busy_end, current_time)
                if overlap_start < overlap_end:
                    total_busy += overlap_end - overlap_start
                
            # Only add to buffer occupancy if the flow is not already fully processed
            if busy_end > current_time:
                if busy_start < current_time:
                    # The flow has been partially processed so must minus that amount from buffer_occupancy
                    buffer_occupancy += flow.flow_size - (current_time - busy_start) * self.capacity_bps
                else:
                    # This flow has not yet started processing so can just add the full flow size
                    buffer_occupancy += flow.flow_size

        utilization = total_busy / interval_length
        stats = {
            self.LINK_UTILIZATION : utilization,
            self.BUFFER_OCCUPANCY : buffer_occupancy
        }

        return stats

    def get_overall_stats(self, current_time: float) -> dict[str, List[Tuple[float, float]]]:
        """
        Calculate the overall stats (link utilization and buffer occupancy) from time 0 up to current_time.
        """
        # Sample utilization at regular intervals
        while self.last_sample_time < current_time:
            stats = self.get_stats(self.last_sample_time, 0)

            for key, attr_name in self.stats_keys.items():
                getattr(self, attr_name).append((self.last_sample_time, stats[key]))
            
            self.last_sample_time += self.sample_interval

        # Construct the return dictionary dynamically using `stats_keys`
        stats_dict = {key: getattr(self, attr_name) for key, attr_name in self.stats_keys.items()}
        return stats_dict
