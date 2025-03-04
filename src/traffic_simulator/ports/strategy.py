import random
from abc import ABC, abstractmethod
import statistics
import numpy as np

from traffic_simulator.config.models import MainConfig
from traffic_simulator.flows.distribution import Distribution
from traffic_simulator.metrics.metric_manager import LinkMetricsTracker
from traffic_simulator.models.flow import Flow
from traffic_simulator.ports.link import Link
from traffic_simulator.flows.flow_size_generator import FlowSizeGenerator
from traffic_simulator.models.event import FlowArrivalEvent

class LoadBalanceStrategy(ABC):
    def __init__(self, links: list[Link]):
        self.links = links

    @abstractmethod
    def select_link(self) -> Link:
        """Choose which link to send the packet on."""
        pass
    
    def select_link_for_flow(self, flow: Flow) -> Link:
        """Choose which link to send the flow on based on its characteristics.
        Default implementation simply calls select_link()."""
        return self.select_link()


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

    def select_link(self, event: FlowArrivalEvent) -> Link:
        """Choose the link most below its target utilization, or least congested if none are under target."""
        most_underutilized = self._find_most_underutilized_link()
        if (most_underutilized):
            return most_underutilized

        return min(self.links, key=lambda link: link.busy_until)

class PercentileBasedStrategy(LoadBalanceStrategy):
    def __init__(
        self,
        links: list[Link],
        link_metric_tracker: LinkMetricsTracker,
        flow_size_generator: FlowSizeGenerator,
    ):
        super().__init__(links)
        self.link_metric_tracker = link_metric_tracker
        self.flow_size_generator = flow_size_generator

        # Compute target utilizations once since the workload is static
        self.target_utilizations = self._compute_target_utilizations()

    def _compute_target_utilizations(self) -> dict[Link, float]:
        num_links = len(self.links)

        # Step 1: Sample flow sizes at 100 evenly spaced percentiles
        probabilities = np.linspace(0.00, 1.00, 100)
        flow_sizes = [self.flow_size_generator.generate_with_probability(p) for p in probabilities]

        # Step 2: Compute the total flow size across all sampled points
        total_flow_size = sum(flow_sizes)

        # Step 3: Compute cumulative flow contributions
        cumulative_flow_sizes = np.cumsum(flow_sizes)  # Running sum of flow sizes
        normalized_cumulative = cumulative_flow_sizes / total_flow_size  # Normalize to [0,1]

        # Step 4: Find the point where X% of total traffic is reached (e.g., 50%)

        # choose 50% since then it balances out so 50% of data is wcmp and 50% of data is least congested
        # this way, averages out to 0 variance since wcmp will make it so there is variance but least congested balance it out

        large_flow_threshold_index = np.searchsorted(normalized_cumulative, 0.05)  # Find 50% contribution point
        self.large_flow_threshold = flow_sizes[min(large_flow_threshold_index - 1, len(flow_sizes) - 1)]  # Get the flow size at this index
        # print(f"large flow threshold: {large_flow_threshold_index} has size {self.large_flow_threshold}")

        # Step 5: Determine per-link allocation threshold
        per_link_flow = total_flow_size / num_links

        # Step 6: Assign links based on cumulative flow size
        target_utilizations = {}
        cumulative_flow = 0.0
        link_index = 0
        threshold = per_link_flow

        for flow_size, probability in zip(flow_sizes, probabilities):
            cumulative_flow += flow_size
            # print(f"probability: {probability}, cumulative flow size: {cumulative_flow}")

            while cumulative_flow >= threshold and link_index < num_links:
                link = self.links[link_index]
                # print(f"threshold: {threshold}, link_index: {link_index}")

                # Compute utilization as complementary fraction of flow range
                utilization_fraction = probability  # Since probability is already cumulative
                complementary_utilization_fraction = 1.0 - utilization_fraction
                target_utilizations[link] = complementary_utilization_fraction

                # Move to the next threshold
                threshold += per_link_flow
                link_index += 1

            if link_index >= num_links:
                break  # Stop if all links have been assigned

        # Step 7: If all target utilizations sum to 0, assign 1.0 to all links
        if sum(target_utilizations.values()) == 0:
            for link in self.links:
                target_utilizations[link] = 1.0

        # normalize target utilizations
        total_utilization = sum(target_utilizations.values())
        target_utilizations = {link: util / total_utilization for link, util in target_utilizations.items()}

        # print(f"target utilizations: {target_utilizations}")

        return target_utilizations

    def get_current_utilization(self, link):
        samples = self.link_metric_tracker.get_link_metric_samples(
            link, "link_utilization"
        )
        if not samples:
            return float("-inf")

        current_utilization = samples[-1][1]
        return current_utilization
    
    def select_link_for_flow(self, flow: Flow) -> Link:
        """Choose a link based on target utilization and flow size."""
        flow_size = flow.flow_size
        current_utilizations = {
            link: self.get_current_utilization(link) for link in self.links
        }

        # print(f"flow size {flow_size},large threshold: {self.large_flow_threshold}")

        if flow_size >= self.large_flow_threshold:
            # For large flows, assign to the link with the lowest current utilization
            # print(f"current utilizations: {current_utilizations}, assigning to lowest which is {min(self.links, key=lambda link: current_utilizations.get(link, float("inf")))}")
            return min(self.links, key=lambda link: current_utilizations.get(link, float("inf")))

        # For normal flows, assign based on target utilization
        return random.choices(self.links, weights=[self.target_utilizations[link] for link in self.links])[0]
    
    def select_link(self) -> Link:
        """Default implementation when flow information isn't available."""
        current_utilizations = {
            link: self.get_current_utilization(link) for link in self.links
        }
        return min(self.links, key=lambda link: current_utilizations.get(link, float("inf")))

class UnevenLoadBalancingStrategy(LoadBalanceStrategy):
    def __init__(
        self,
        links: list[Link],
        link_metric_tracker: LinkMetricsTracker,
        config: MainConfig,
        buffer_link_indices: list[int] | None = None,
        percentile_threshold: float = 95.0,
        distribution: Distribution | None = None,
    ):
        super().__init__(links)
        # Default: use 20% of links as buffer links if not specified
        self.buffer_link_indices = buffer_link_indices or list(range(len(links) // 5))
        self.buffer_links = [links[i] for i in self.buffer_link_indices]
        self.normal_links = [link for i, link in enumerate(links) if i not in self.buffer_link_indices]
        self.link_metric_tracker = link_metric_tracker
        self.config = config
        self.percentile_threshold = percentile_threshold
        self.distribution = distribution
    
    def get_flow_size_threshold(self):
        """Calculate the threshold for routing to buffer links"""
        return self.distribution.percentile(self.percentile_threshold)
    
    def select_link_for_flow(self, flow: Flow) -> Link:
        """Choose which link to send the flow on based on its size."""
        threshold = self.get_flow_size_threshold()
        
        if flow.flow_size > threshold:
            # Large flow: route to least loaded buffer link
            if self.buffer_links:
                return min(self.buffer_links, key=lambda link: link.busy_until)
            else:
                # Fallback if no buffer links defined
                return min(self.links, key=lambda link: link.busy_until)
        else:
            # Normal flow: use WCMPSrategy on all links
            weights = [link.target_utilization for link in self.config.network.links]
            return WCMPSrategy(self.links, weights).select_link()
    
    def select_link(self) -> Link:
        """Default implementation when flow information isn't available."""
        return min(self.links, key=lambda link: link.busy_until)


class StrategyFactory:
    @staticmethod
    def create_strategy(
        strategy_name: str,
        links: list[Link],
        config: MainConfig,
        link_metric_tracker: LinkMetricsTracker,
        flow_size_generator: FlowSizeGenerator,
        distribution: Distribution | None = None,
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
        elif strategy_name == "percentile_based":
            return PercentileBasedStrategy(links, link_metric_tracker, flow_size_generator)
        elif strategy_name == "uneven":
            buffer_link_indices = getattr(config.network, "buffer_link_indices", None)
            percentile_threshold = getattr(config.network, "large_flow_percentile", 95.0)
            return UnevenLoadBalancingStrategy(
                links, link_metric_tracker, config, 
                buffer_link_indices, percentile_threshold, distribution
            )
        else:
            raise ValueError(f"Invalid strategy name: {strategy_name}")
