import click
import pathlib

from traffic_simulator.config.config_loader import load_config
from traffic_simulator.flows.flow_generator import PoissonFlowGenerator
from traffic_simulator.flows.flow_size_generator import FlowSizeGeneratorFactory
from traffic_simulator.ports.link import Link
from traffic_simulator.ports.strategy import StrategyFactory
from traffic_simulator.simulator.simulator import Simulator


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    default="config.yaml",
    help="Path to the YAML configuration file",
)
@click.option(
    "--output",
    type=click.Path(),
    default="output",
    help="Path to the output directory",
)
def cli(config: str, output: str):
    # Create the output directory if it does not exist
    pathlib.Path(output).mkdir(parents=True, exist_ok=True)

    # Load the configuration file
    sim_config = load_config(config)

    flow_size_generator = FlowSizeGeneratorFactory.create_generator(sim_config)
    flow_generator = PoissonFlowGenerator(
        arrival_rate=sim_config.traffic.flow_arrival.rate,
        flow_size_generator=flow_size_generator,
    )

    links = [Link(capacity_bps=link.capacity) for link in sim_config.network.links]
    strategy = StrategyFactory.create_strategy(
        strategy_name=sim_config.network.strategy,
        links=links,
        config=sim_config,
    )

    simulator = Simulator(
        duration=sim_config.simulation.duration,
        flow_generator=flow_generator,
        strategy=strategy,
        links=links,
    )
    simulator.run()
    simulator.visualize(save_path=output)
