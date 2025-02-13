import random
from abc import ABC, abstractmethod

from traffic_simulator.config.models import MainConfig
from traffic_simulator.metrics.metric_manager import LinkMetricsTracker
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


class MostUnderTargetStrategy(LoadBalanceStrategy):
    def __init__(self, links: list[Link], link_metric_tracker: LinkMetricsTracker, config: MainConfig):
        super().__init__(links)
        self.link_metric_tracker = link_metric_tracker
        self.config = config
        
    def select_link(self) -> Link:
        # Choose the link that is most under its target utilization, otherwise choose the least congested link
        least_utilized_link = None
        least_utilized_diff = float("inf")
        
        for i in range(len(self.config.network.links)):
            link = self.links[i]
            samples = self.link_metric_tracker.get_link_metric_samples(link, "link_utilization")
            if not samples:
                continue
            actual_utilization = samples[-1][1]
            target_utilization = self.config.network.links[i].target_utilization
            diff = target_utilization - actual_utilization
            if diff > 0 and diff < least_utilized_diff:
                least_utilized_diff = diff
                least_utilized_link = link
            
        if least_utilized_link:
            return least_utilized_link
        else:
            return min(self.config.network.links, key=lambda link: link.busy_until)
    
class StrategyFactory:
    @staticmethod
    def create_strategy(
        strategy_name: str, links: list[Link], config: MainConfig, link_metric_tracker: LinkMetricsTracker
    ) -> LoadBalanceStrategy:
        if strategy_name == "ecmp":
            return ECMPStrategy(links)
        elif strategy_name == "wcmp":
            weights = [link.target_utilization for link in config.network.links]
            return WCMPSrategy(links, weights)
        elif strategy_name == "least_congested":
            return LeastCongestedStrategy(links)
        elif strategy_name == "most_under_target":
            return MostUnderTargetStrategy(links, link_metric_tracker, config)
        else:
            raise ValueError(f"Invalid strategy name: {strategy_name}")
