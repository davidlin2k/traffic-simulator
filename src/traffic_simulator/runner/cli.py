import click

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
def cli(config: str):
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
