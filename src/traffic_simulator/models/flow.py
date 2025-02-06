from dataclasses import dataclass


@dataclass
class Flow:
    id: int
    arrival_time: float
    flow_size: int
    processing_start_time: float = 0.0
    processing_end_time: float = 0.0
    assigned_port: int | None = None
    assigned_server: int | None = None
