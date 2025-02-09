from abc import ABC, abstractmethod
import random

from traffic_simulator.config.models import (
    BoundedParetoParams,
    MainConfig,
)
from traffic_simulator.flows.distribution import BoundedParetoDistribution, Distribution


class FlowSizeGenerator(ABC):
    @abstractmethod
    def generate(self) -> int:
        pass


class ConstantFlowSizeGenerator(FlowSizeGenerator):
    def __init__(self, flow_size: int):
        self.flow_size = flow_size

    def generate(self) -> int:
        return self.flow_size


class UniformFlowSizeGenerator(FlowSizeGenerator):
    def __init__(self, min_flow_size: int, max_flow_size: int):
        self.min_flow_size = min_flow_size
        self.max_flow_size = max_flow_size

    def generate(self) -> int:
        return random.randint(self.min_flow_size, self.max_flow_size)


class QuantileFlowSizeGenerator(FlowSizeGenerator):
    def __init__(self, distribution: Distribution):
        self.distribution = distribution

    def generate(self) -> int:
        u = random.random()
        return self.distribution.quantile(u)


class FlowSizeGeneratorFactory:
    # Mapping from generator type to the generator class
    _generator_mapping = {
        "constant": ConstantFlowSizeGenerator,
        "uniform": UniformFlowSizeGenerator,
        "quantile": QuantileFlowSizeGenerator,
    }

    @classmethod
    def create_generator(cls, config: MainConfig) -> FlowSizeGenerator:
        if config.traffic.flow_size.type == "bounded_pareto":
            if not isinstance(config.traffic.flow_size.params, BoundedParetoParams):
                raise ValueError("Invalid parameters for Bounded Pareto.")

            distribution = BoundedParetoDistribution(
                lower_bound=config.traffic.flow_size.params.lower,
                upper_bound=config.traffic.flow_size.params.upper,
                alpha=config.traffic.flow_size.params.alpha,
            )
            return QuantileFlowSizeGenerator(distribution)

        elif config.traffic.flow_size.type == "uniform":

            return UniformFlowSizeGenerator(
                min_flow_size=config.traffic.flow_size.params["min_flow_size"],
                max_flow_size=config.traffic.flow_size.params["max_flow_size"],
            )

        else:
            raise ValueError(
                f"Unsupported flow size generator type: {config.traffic.flow_size.type}"
            )
