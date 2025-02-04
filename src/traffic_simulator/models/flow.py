from dataclasses import dataclass


@dataclass
class Flow:
    id: int
    arrival_time: float
    flow_size: int
    assigned_port: int | None = None
    assigned_server: int | None = None
