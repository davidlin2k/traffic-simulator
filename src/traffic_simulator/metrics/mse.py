from typing import List, Dict
import numpy as np
from traffic_simulator.ports.link import Link
from traffic_simulator.config.models import LinkConfig
from traffic_simulator.metrics.metric_manager import LinkMetricsTracker


def calculate_mse(
    metrics_tracker: LinkMetricsTracker,
    links: List[Link],
    link_configs: List[LinkConfig],
    current_time: float,
) -> float:
    """
    Calculate Mean Square Error between target and actual link utilizations.

    Args:
        metrics_tracker: LinkMetricsTracker instance managing the metrics
        links: List of Link objects
        link_configs: List of LinkConfig objects containing target utilizations
        current_time: Current simulation time

    Returns:
        float: Mean Square Error value
    """
    squared_errors = []

    for link, config in zip(links, link_configs):
        # Get actual utilization from the metrics tracker
        samples = metrics_tracker.get_link_metric_samples(link, "link_utilization")
        if not samples:
            continue
        actual_utilization = samples[-1][1]  # Get latest sample
        target_utilization = config.target_utilization

        # Calculate squared error
        error = actual_utilization - target_utilization
        squared_errors.append(error**2)

    if not squared_errors:
        return 0.0

    # Calculate mean of squared errors
    mse = np.mean(squared_errors)
    return mse


def calculate_per_link_errors(
    metrics_tracker: LinkMetricsTracker,
    links: List[Link],
    link_configs: List[LinkConfig],
    current_time: float,
) -> Dict[str, float]:
    """
    Calculate squared error for each link individually.

    Args:
        metrics_tracker: LinkMetricsTracker instance managing the metrics
        links: List of Link objects
        link_configs: List of LinkConfig objects containing target utilizations
        current_time: Current simulation time

    Returns:
        Dict[str, float]: Dictionary mapping link IDs to their squared errors
    """
    errors = {}

    for link, config in zip(links, link_configs):
        samples = metrics_tracker.get_link_metric_samples(link, "link_utilization")
        if not samples:
            errors[config.id] = 0.0
            continue

        actual_utilization = samples[-1][1]  # Get latest sample
        target_utilization = config.target_utilization

        error = actual_utilization - target_utilization
        errors[config.id] = error**2

    return errors
