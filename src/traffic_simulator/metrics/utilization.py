from traffic_simulator.models.flow import Flow


def calculate_link_utilization_multiple(
    flows: list[Flow],
    link_capacities: dict[int, float],
    simulation_time: float
) -> dict[int, float]:
    """
    Calculates the utilization for each link.
    
    Parameters:
        flows: List of Flow objects (flow_size should be in bits and assigned_port denotes the link id).
        link_capacities: A dictionary mapping link ids to their capacities (in bits per second).
        simulation_time: Total simulation time in seconds.
    
    Returns:
        A dictionary mapping each link id to its utilization (as a fraction between 0 and 1).
    """
    # Initialize a dictionary to store total data transmitted per link
    link_data = [0] * len(link_capacities)
    for flow in flows:
        if flow.assigned_port is not None:
            link_data[flow.assigned_port] += flow.flow_size

    utilizations = {}
    for i, total_data in enumerate(link_data):
        capacity = link_capacities[i]
        max_possible_data = capacity * simulation_time
        utilizations[i] = total_data / max_possible_data
    return utilizations