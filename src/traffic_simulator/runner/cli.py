import click

from traffic_simulator.config.config_loader import load_config
from traffic_simulator.flows.distribution import BoundedParetoDistribution
from traffic_simulator.flows.flow_generator import PoissonFlowGenerator
from traffic_simulator.flows.flow_size_generator import FlowSizeGeneratorFactory
from traffic_simulator.simulator.simulator import Simulator


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
        arrival_rate=sim_config.arrival_rate, flow_size_generator=flow_size_generator
    )

    simulator = Simulator(
        simulation_time=sim_config.simulation_time,
        flow_generator=flow_generator,
    )
    simulator.run()
    simulator.visualize_flows_scatter()
