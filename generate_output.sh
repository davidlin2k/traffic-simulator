#!/bin/bash

# Create output directory if it doesn't exist
mkdir -p output

# Run websearch workload configurations
echo "Running websearch workload simulations..."
traffic-simulator --config configs/websearch_wcmp.yaml --output ./output/websearch_wcmp
traffic-simulator --config configs/websearch_ecmp.yaml --output ./output/websearch_ecmp
traffic-simulator --config configs/websearch_mut.yaml --output ./output/websearch_mut
traffic-simulator --config configs/websearch_lc.yaml --output ./output/websearch_lc

# Run datamining workload configurations
echo "Running datamining workload simulations..."
traffic-simulator --config configs/datamining_wcmp.yaml --output ./output/datamining_wcmp
traffic-simulator --config configs/datamining_ecmp.yaml --output ./output/datamining_ecmp
traffic-simulator --config configs/datamining_mut.yaml --output ./output/datamining_mut
traffic-simulator --config configs/datamining_lc.yaml --output ./output/datamining_lc

# Run ML workload configurations
echo "Running ML workload simulations..."
traffic-simulator --config configs/ML_wcmp.yaml --output ./output/ML_wcmp
traffic-simulator --config configs/ML_ecmp.yaml --output ./output/ML_ecmp
traffic-simulator --config configs/ML_mut.yaml --output ./output/ML_mut
traffic-simulator --config configs/ML_lc.yaml --output ./output/ML_lc

echo "All simulations completed!"
