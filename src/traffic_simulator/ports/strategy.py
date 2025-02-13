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
    def __init__(
        self,
        links: list[Link],
        link_metric_tracker: LinkMetricsTracker,
        config: MainConfig,
    ):
        super().__init__(links)
        self.link_metric_tracker = link_metric_tracker
        self.config = config

    def _get_utilization_gap(self, link: Link, link_config) -> float:
        """Calculate how far a link is below its target utilization."""
        samples = self.link_metric_tracker.get_link_metric_samples(
            link, "link_utilization"
        )
        if not samples:
            return float("-inf")

        current_utilization = samples[-1][1]
        return link_config.target_utilization - current_utilization

    def _find_most_underutilized_link(self) -> Link | None:
        """Find the link with the largest positive gap to its target utilization."""
        utilization_gaps = [
            (link, self._get_utilization_gap(link, link_config))
            for link, link_config in zip(self.links, self.config.network.links)
        ]

        valid_gaps = [(link, gap) for link, gap in utilization_gaps if gap > 0]
        if not valid_gaps:
            return None

        return max(valid_gaps, key=lambda x: x[1])[0]

    def select_link(self) -> Link:
        """Choose the link most below its target utilization, or least congested if none are under target."""
        most_underutilized = self._find_most_underutilized_link()
        if most_underutilized:
            return most_underutilized

        return min(self.links, key=lambda link: link.busy_until)


class StrategyFactory:
    @staticmethod
    def create_strategy(
        strategy_name: str,
        links: list[Link],
        config: MainConfig,
        link_metric_tracker: LinkMetricsTracker,
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
