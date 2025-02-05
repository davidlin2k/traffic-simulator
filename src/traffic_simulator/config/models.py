# config_models.py
from pydantic import BaseModel, Field
from typing import Dict, Optional, Union


class BoundedParetoConfig(BaseModel):
    alpha: float = Field(..., description="Pareto shape parameter (alpha)")
    lower: float = Field(..., description="Lower bound for the distribution")
    upper: float = Field(..., description="Upper bound for the distribution")


class UniformFlowSizeConfig(BaseModel):
    min_flow_size: float = Field(..., description="Minimum flow size")
    max_flow_size: float = Field(..., description="Maximum flow size")


class FlowSizeGenConfig(BaseModel):
    type: str = Field(..., description="Type of flow size generator")
    params: Union[BoundedParetoConfig, UniformFlowSizeConfig]

class SimulatorConfig(BaseModel):
    simulation_time: float = Field(..., description="Total simulation time")
    arrival_rate: float = Field(..., description="Flow arrival rate")
    flow_size_gen: FlowSizeGenConfig = Field(
        ..., description="Flow size generator configuration"
    )
    link_capacities: list[float] = Field(
        ..., description="List of link capacities (in bits per second)"
    )
