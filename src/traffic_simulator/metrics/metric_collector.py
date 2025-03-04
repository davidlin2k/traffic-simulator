from abc import ABC, abstractmethod


class MetricCollector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this metric"""
        pass

    @abstractmethod
    def collect(self, link, current_time: float) -> float:
        """Return a metric value given a link context and current time"""
        pass


class UtilizationCollector(MetricCollector):
    @property
    def name(self) -> str:
        return "link_utilization"

    def collect(self, link, current_time: float) -> float:
        if current_time <= 0:
            return 0.0

        total_busy = sum(
            min(flow.end_time, current_time) - max(flow.start_time, 0.0)
            for flow in link.flows
            if flow.end_time > 0.0 and flow.start_time < current_time
        )

        return total_busy / current_time


class BufferOccupancyCollector(MetricCollector):
    @property
    def name(self) -> str:
        return "buffer_occupancy"

    def collect(self, link, current_time: float) -> float:
        return sum(
            link._get_remaining_flow_size(flow, current_time)
            for flow in link.queue
            if flow.end_time > current_time
        )


class FlowCompletionTimeCollector(MetricCollector):
    @property
    def name(self) -> str:
        return "flow_completion_time"

    def collect(self, link, current_time: float) -> float:
        if not link.flows:
            return 0.0

        return sum(
            flow.end_time - flow.arrival_time
            for flow in link.flows
            if flow.end_time > 0.0
        ) / len(link.flows)

