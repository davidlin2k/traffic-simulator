import numpy as np

def calculate_bounded_pareto_mean(lower: float, upper: float, alpha: float) -> float:
    """Calculate the theoretical mean of a Bounded Pareto distribution."""
    if alpha != 1:
        numerator = (lower**alpha) * (alpha/(alpha-1)) * (1/(lower**(alpha-1)) - 1/(upper**(alpha-1)))
        denominator = 1 - (lower/upper)**alpha
        return numerator / denominator
    else:
        # Special case for alpha = 1
        return (upper*lower/(upper-lower)) * np.log(upper/lower)

def calculate_dynamic_lambda(params, links, target_utilization: float = 0.8) -> float:
    """
    Calculate dynamic lambda based on target utilization:
    λ = (target_utilization × total_link_capacity) ÷ average_flow_size
    """
    # Get total link capacity
    total_link_capacity = sum(link.capacity_bps for link in links)
    
    # Calculate mean flow size using the Bounded Pareto formula
    avg_flow_size = calculate_bounded_pareto_mean(params.lower, params.upper, params.alpha)
    
    # Calculate dynamic lambda
    dynamic_lambda = (target_utilization * total_link_capacity) / avg_flow_size
    
    return dynamic_lambda