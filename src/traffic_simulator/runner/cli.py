import click

from traffic_simulator.flows.flow_generator import PoissonFlowGenerator
from traffic_simulator.flows.flow_size_generator import FlowSizeGeneratorFactory
from traffic_simulator.simulator.simulator import Simulator


@click.command()
@click.option("--simulation-time", type=float, default=10.0)
@click.option("--arrival-rate", type=float, default=5.0)
@click.option("--flow-size-gen-type", type=str, default="uniform")
def cli(simulation_time, arrival_rate, flow_size_gen_type):
    flow_size_params = {"min_flow_size": 10, "max_flow_size": 100}
    flow_size_generator = FlowSizeGeneratorFactory.create_generator(
        flow_size_gen_type, **flow_size_params
    )

    flow_generator = PoissonFlowGenerator(
        arrival_rate=arrival_rate, flow_size_generator=flow_size_generator
    )

    simulator = Simulator(
        simulation_time=simulation_time,
        flow_generator=flow_generator,
    )
    simulator.run()
    simulator.visualize_flows_scatter()
