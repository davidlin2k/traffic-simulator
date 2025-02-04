from abc import ABC, abstractmethod
import random


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


class CDFFlowSizeGenerator(FlowSizeGenerator):
    def __init__(self, cdf: dict[int, float]):
        self.cdf = cdf

    def generate(self) -> int:
        random_number = random.random()
        for flow_size, probability in self.cdf.items():
            if random_number < probability:
                return flow_size
            random_number -= probability
        return flow_size


class FlowSizeGeneratorFactory:
    # Mapping from generator type to the generator class
    _generator_mapping = {
        "constant": ConstantFlowSizeGenerator,
        "uniform": UniformFlowSizeGenerator,
        "cdf": CDFFlowSizeGenerator,
    }

    @classmethod
    def create_generator(cls, generator_type: str, **kwargs) -> FlowSizeGenerator:
        try:
            generator_cls = cls._generator_mapping[generator_type]
        except KeyError:
            raise ValueError(f"Unknown generator type: {generator_type}")
        return generator_cls(**kwargs)
