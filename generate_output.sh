#!/bin/bash

# Array of configuration files
configs=("./configs/config.yaml")

# Loop through each configuration file and call traffic-simulator
for config in "${configs[@]}"; do
  echo "Running traffic-simulator with $config"
  traffic-simulator --config "$config" --output "./output/$(basename "$config" .yaml)"
done
