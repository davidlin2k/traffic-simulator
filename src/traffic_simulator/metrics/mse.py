from typing import List, Dict
import numpy as np
from traffic_simulator.ports.link import Link
from traffic_simulator.config.models import LinkConfig

def calculate_mse(links: List[Link], link_configs: List[LinkConfig], current_time: float) -> float:
    """
    Calculate Mean Square Error between target and actual link utilizations.
    
    Args:
        links: List of Link objects with current utilization data
        link_configs: List of LinkConfig objects containing target utilizations
        current_time: Current simulation time
    
    Returns:
        float: Mean Square Error value
    """
    squared_errors = []
    
    for link, config in zip(links, link_configs):
        # Get actual utilization for the link
        actual_utilization = link.metrics.utilization_samples[-1][1]
        target_utilization = config.target_utilization
        
        # Calculate squared error
        error = actual_utilization - target_utilization
        squared_errors.append(error ** 2)
    
    # Calculate mean of squared errors
    mse = np.mean(squared_errors)
    return mse

def calculate_per_link_errors(links: List[Link], link_configs: List[LinkConfig], current_time: float) -> Dict[str, float]:
    """
    Calculate squared error for each link individually.
    
    Args:
        links: List of Link objects with current utilization data
        link_configs: List of LinkConfig objects containing target utilizations
        current_time: Current simulation time
    
    Returns:
        Dict[str, float]: Dictionary mapping link IDs to their squared errors
    """
    errors = {}
    
    for link, config in zip(links, link_configs):
        actual_utilization = link.metrics.utilization_samples[-1][1]
        target_utilization = config.target_utilization
        
        error = actual_utilization - target_utilization
        errors[config.id] = error ** 2
    
    return errors