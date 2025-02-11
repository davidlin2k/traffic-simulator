from dataclasses import dataclass


@dataclass
class Flow:
    id: int
    arrival_time: float
    flow_size: int
    start_time: float = 0.0
    end_time: float = 0.0
