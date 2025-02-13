from typing import Any
from traffic_simulator.metrics.metric_collector import MetricCollector

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
