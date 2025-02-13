from typing import Any

from traffic_simulator.ports.link import Link
from traffic_simulator.metrics.metric_collector import BufferOccupancyCollector, FlowCompletionTimeCollector, MetricCollector, UtilizationCollector


class MetricsManager:
    def __init__(self):
        self._collectors: dict[str, MetricCollector] = {}
        self.samples: dict[str, list[tuple[float, float]]] = {}

    def register(self, collector: MetricCollector) -> None:
        self._collectors[collector.name] = collector
        self.samples[collector.name] = []

    def sample_all(self, link: Any, timestamp: float) -> None:
        for collector in self._collectors.values():
            value = collector.collect(link, timestamp)
            self.samples[collector.name].append((timestamp, value))

class LinkMetricsTracker:
    def __init__(self, sample_interval: float = 1.0):
        self.sample_interval = sample_interval
        self.link_metrics: dict[Link, MetricsManager] = {}
        self.last_sample_times: dict[Link, float] = {}

    def register_link(self, link: Link) -> None:
        """Register a new link to track metrics for"""
        metrics_manager = MetricsManager()
        metrics_manager.register(UtilizationCollector())
        metrics_manager.register(BufferOccupancyCollector())
        metrics_manager.register(FlowCompletionTimeCollector())
        
        self.link_metrics[link] = metrics_manager
        self.last_sample_times[link] = 0.0

    def sample_metrics(self, current_time: float) -> None:
        """Sample metrics for all registered links"""
        for link, metrics_manager in self.link_metrics.items():
            last_sample = self.last_sample_times[link]
            while last_sample < current_time:
                metrics_manager.sample_all(link, last_sample)
                last_sample += self.sample_interval
            self.last_sample_times[link] = last_sample

    def get_link_metric_samples(self, link: Link, metric_name: str):
        """Get samples for a specific metric from a specific link"""
        if link in self.link_metrics:
            return self.link_metrics[link].samples.get(metric_name, [])
        return []
    