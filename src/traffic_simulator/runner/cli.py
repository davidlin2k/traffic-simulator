import random
import click
import pathlib

from traffic_simulator.config.config_loader import load_config
from traffic_simulator.flows.distribution import DistributionFactory
from traffic_simulator.flows.flow_generator import PoissonFlowGenerator
from traffic_simulator.flows.flow_size_generator import FlowSizeGeneratorFactory
from traffic_simulator.metrics.metric_manager import LinkMetricsTracker
from traffic_simulator.ports.link import Link
from traffic_simulator.ports.strategy import StrategyFactory
from traffic_simulator.simulator.simulator import Simulator

random.seed(42)

@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True),
    default="configs/config.yaml",
    help="Path to the YAML configuration file",
)
@click.option(
    "--output",
    type=click.Path(),
    default="output",
    help="Path to the output directory",
)
@click.option(
    "--dynamic-lambda",
    is_flag=True,
    default=False,
    help="Use dynamic lambda calculation",
)
def cli(config: str, output: str, dynamic_lambda: bool):
    # Create the output directory if it does not exist
    pathlib.Path(output).mkdir(parents=True, exist_ok=True)

    # Load the configuration file
    sim_config = load_config(config)
    
    distribution = DistributionFactory.create_distribution(distribution_type=sim_config.traffic.flow_size.type, params=sim_config.traffic.flow_size.params)

    flow_size_generator = FlowSizeGeneratorFactory.create_generator(sim_config, distribution)

    # Calculate dynamic lambda if requested
    arrival_rate = sim_config.traffic.flow_arrival.rate
    if dynamic_lambda:
        from traffic_simulator.flows.lambda_calculator import calculate_dynamic_lambda
        links = [Link(capacity_bps=link.capacity) for link in sim_config.network.links]
        arrival_rate = calculate_dynamic_lambda(
            sim_config.traffic.flow_size.params,
            links
        )

    print(f"Dynamic lambda calculated: {arrival_rate:.2f} (vs. config: {sim_config.traffic.flow_arrival.rate:.2f})")

    flow_generator = PoissonFlowGenerator(
        arrival_rate=sim_config.traffic.flow_arrival.rate,
        flow_size_generator=flow_size_generator,
    )

    links = [Link(capacity_bps=link.capacity) for link in sim_config.network.links]
    links_metric_tracker = LinkMetricsTracker(
        sim_config.simulation.metrics.sample_interval
    )
    for link in links:
        links_metric_tracker.register_link(link)

    strategy = StrategyFactory.create_strategy(
        strategy_name=sim_config.network.strategy,
        links=links,
        config=sim_config,
        link_metric_tracker=links_metric_tracker,
        flow_size_generator=flow_size_generator,
        distribution=distribution,
    )

    simulator = Simulator(
        duration=sim_config.simulation.duration,
        flow_generator=flow_generator,
        flow_size_generator=flow_size_generator,
        strategy=strategy,
        links=links,
        link_configs=sim_config.network.links,
        link_metric_tracker=links_metric_tracker,
    )
    simulator.run()
    simulator.visualize(save_path=output)
