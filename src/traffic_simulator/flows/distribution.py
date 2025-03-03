from abc import ABC, abstractmethod

from traffic_simulator.config.models import BoundedParetoParams


class Distribution(ABC):
    @abstractmethod
    def quantile(self, u: float) -> int:
        """
        Given a uniform random variable u in [0, 1], return a sample
        from the distribution.
        """
        pass
    
    def percentile(self, p: float) -> int:
        """
        Return the value at the given percentile p (0-100).
        
        :param p: Percentile (0-100)
        :return: Value at the given percentile
        """
        if not 0 <= p <= 100:
            raise ValueError("Percentile must be between 0 and 100")
        return self.quantile(p / 100)


class BoundedParetoDistribution(Distribution):
    def __init__(self, lower_bound: float, upper_bound: float, alpha: float):
        """
        :param lower_bound: The minimum value (L).
        :param upper_bound: The maximum value (U).
        :param alpha: The shape parameter.
        """
        self.L = lower_bound
        self.U = upper_bound
        self.alpha = alpha

    def quantile(self, u: float) -> int:
        """
        The bounded Pareto CDF is given by:
            F(x) = (1 - (L/x)^alpha) / (1 - (L/U)^alpha)
        Solving F(x) = u for x, we get the quantile function:
            x = L / (1 - u * (1 - (L/U)**alpha))^(1/alpha)
        """
        denominator = (1 - u * (1 - (self.L / self.U) ** self.alpha)) ** (
            1 / self.alpha
        )
        x = self.L / denominator
        return int(x)


class DistributionFactory:
    _distribution_mapping = {
        "bounded_pareto": BoundedParetoDistribution,
    }

    @classmethod
    def create_distribution(cls, distribution_type: str, params: BoundedParetoParams | dict) -> Distribution:
        if distribution_type not in cls._distribution_mapping:
            raise ValueError(f"Unknown distribution type: {distribution_type}")

        if distribution_type == "bounded_pareto":
            if not isinstance(params, BoundedParetoParams):
                raise ValueError("Invalid parameters for Bounded Pareto.")
            
            return BoundedParetoDistribution(
                lower_bound=params.lower,
                upper_bound=params.upper,
                alpha=params.alpha,
            )
        
        raise ValueError(f"Unsupported distribution type: {distribution_type}")
    