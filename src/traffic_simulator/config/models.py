from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator
from pathlib import Path


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: Optional[str] = None


class MetricsConfig(BaseModel):
    enabled: bool = True
    sample_interval: float = 1.0

    @field_validator("sample_interval")
    def validate_interval(cls, v):
        if v <= 0:
            raise ValueError("Sample interval must be positive")
        return v


class SimulationConfig(BaseModel):
    duration: float
    seed: Optional[int] = None
    logging: LoggingConfig = LoggingConfig()
    metrics: MetricsConfig = MetricsConfig()

    @field_validator("duration")
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v


class LinkConfig(BaseModel):
    id: str
    capacity: float
    time_window_duration: float
    target_utilization: float

    @field_validator("capacity")
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @field_validator("time_window_duration")
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @field_validator("target_utilization")
    def validate_positive(cls, v):
        if v < 0 or v > 1.0:
            raise ValueError("Value must be within 0.0 and 1.0")
        return v


class NetworkConfig(BaseModel):
    strategy: Literal[
        "ecmp", 
        "wcmp", 
        "least_congested", 
        "most_under_target", 
        "percentile_based",
        "uneven",
        ]
    links: List[LinkConfig]
    buffer_links: Optional[int] = 0  # Indices of links to use as buffers
    large_flow_percentile: Optional[float] = 99.0  # Percentile threshold for large flows


class PoissonArrivalConfig(BaseModel):
    type: Literal["poisson"]
    rate: float

    @field_validator("rate")
    def validate_rate(cls, v):
        if v <= 0:
            raise ValueError("Rate must be positive")
        return v


class BoundedParetoParams(BaseModel):
    alpha: float
    lower: float
    upper: float

    @field_validator("alpha", "lower", "upper")
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("Parameters must be positive")
        return v

    @field_validator("upper")
    def validate_bounds(cls, v, values):
        if "lower" in values.data and v <= values.data["lower"]:
            raise ValueError("Upper bound must be greater than lower bound")
        return v


class FlowSizeConfig(BaseModel):
    type: Literal["bounded_pareto", "uniform"]
    params: Union[BoundedParetoParams, dict]


class TrafficConfig(BaseModel):
    flow_arrival: PoissonArrivalConfig
    flow_size: FlowSizeConfig


class FlowSizeDistribution(BaseModel):
    """Parameters for the flow size distribution"""
    distribution_type: str = "bounded_pareto"  # bounded_pareto, exponential, etc.
    mean: float = 100.0  # Mean flow size
    alpha: Optional[float] = 1.1  # Shape parameter for Pareto
    min_size: Optional[float] = 10.0  # Minimum flow size for bounded Pareto
    max_size: Optional[float] = 1000.0  # Maximum flow size for bounded Pareto


class MainConfig(BaseModel):
    version: str
    simulation: SimulationConfig
    network: NetworkConfig
    traffic: TrafficConfig
    flow_size_distribution: FlowSizeDistribution = Field(default_factory=FlowSizeDistribution)
