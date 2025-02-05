import yaml
from traffic_simulator.config.models import SimulatorConfig


def load_config(config_file: str) -> SimulatorConfig:
    with open(config_file, "r") as f:
        config_dict = yaml.safe_load(f)
    return SimulatorConfig(**config_dict)
