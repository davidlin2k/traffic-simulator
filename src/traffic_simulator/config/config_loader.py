import yaml
from traffic_simulator.config.models import MainConfig


def load_config(config_file: str) -> MainConfig:
    with open(config_file, "r") as f:
        config_dict = yaml.safe_load(f)
    return MainConfig(**config_dict)
