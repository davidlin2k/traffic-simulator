import random
from abc import ABC, abstractmethod

from traffic_simulator.config.models import MainConfig
from traffic_simulator.models.flow import Flow
from traffic_simulator.ports.link import Link


class LoadBalanceStrategy(ABC):
    def __init__(self, links: list[Link]):
        self.links = links

    @abstractmethod
    def select_link(self) -> Link:
        """Choose which link to send the packet on."""
        pass


class ECMPStrategy(LoadBalanceStrategy):
    def select_link(self) -> Link:
        # Equal-cost multi-path routing
        return random.choice(self.links)


class WCMPSrategy(LoadBalanceStrategy):
    def __init__(self, links: list[Link], weights: list[int]):
        super().__init__(links)
        self.weights = weights

    def select_link(self) -> Link:
        # Weighted multi-path routing
        return random.choices(self.links, weights=self.weights)[0]


class LeastCongestedStrategy(LoadBalanceStrategy):
    def select_link(self) -> Link:
        # Choose the least congested link
        return min(self.links, key=lambda link: link.busy_until)


class StrategyFactory:
    @staticmethod
    def create_strategy(
        strategy_name: str, links: list[Link], config: MainConfig
    ) -> LoadBalanceStrategy:
        if strategy_name == "ecmp":
            return ECMPStrategy(links)
        elif strategy_name == "wcmp":
            weights = [link.target_utilization for link in config.network.links]
            return WCMPSrategy(links, weights)
        elif strategy_name == "least_congested":
            return LeastCongestedStrategy(links)
        else:
            raise ValueError(f"Invalid strategy name: {strategy_name}")
