from abc import ABC, abstractmethod


class Distribution(ABC):
    @abstractmethod
    def quantile(self, u: float) -> int:
        """
        Given a uniform random variable u in [0, 1], return a sample
        from the distribution.
        """
        pass


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
