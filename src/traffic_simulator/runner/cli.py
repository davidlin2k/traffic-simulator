import click

from traffic_simulator.config.config_loader import load_config
from traffic_simulator.flows.flow_generator import PoissonFlowGenerator
from traffic_simulator.flows.flow_size_generator import FlowSizeGeneratorFactory
from traffic_simulator.ports.port_assigner import UniformPortAssigner, WeightedPortAssigner, LeastMSEPortAssigner
from traffic_simulator.simulator.simulator import Simulator
from traffic_simulator.ports.port import Port
from traffic_simulator.ports.port_manager import PortManager


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    default="config.yaml",
    help="Path to the YAML configuration file",
)
def cli(config: str):
    sim_config = load_config(config)

    flow_size_generator = FlowSizeGeneratorFactory.create_generator(sim_config)
    flow_generator = PoissonFlowGenerator(
        arrival_rate=sim_config.traffic.flow_arrival.rate, flow_size_generator=flow_size_generator
    )

    link_capacities = [link_config.capacity for link_config in sim_config.network.links]
    link_time_window_durations = [link_config.time_window_duration for link_config in sim_config.network.links]
    target_utilizations = [link_config.target_utilization for link_config in sim_config.network.links]
    port_ids = list(range(len(link_capacities)))
    ports = [
        Port(id=link_id, max_capacity=link_capacities[link_id], time_window_duration=link_time_window_durations[link_id], target_utilization=target_utilizations[link_id])
        for link_id in port_ids
    ]

    # test
    # port_assigner = UniformPortAssigner(ports)
    # port_assigner = WeightedPortAssigner(ports, [100, 2, 2, 2])
    port_assigner = LeastMSEPortAssigner(ports)



    port_manager = PortManager(ports, port_assigner)

    simulator = Simulator(
        simulation_time=sim_config.simulation.duration,
        flow_generator=flow_generator,
        port_manager=port_manager,
        port_ids=port_ids,
        config_file=config
    )
    simulator.run()
    simulator.visualize_flows_scatter()
