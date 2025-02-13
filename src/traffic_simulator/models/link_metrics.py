from dataclasses import dataclass, field


@dataclass
class LinkMetrics:
    """Container for link metrics"""

    utilization_samples: list[tuple[float, float]] = field(default_factory=list)
    buffer_occupancy_samples: list[tuple[float, float]] = field(default_factory=list)
    flow_completion_times: list[tuple[float, float]] = field(default_factory=list)
    last_sample_time: float = 0.0
    sample_interval: float = 0.1
