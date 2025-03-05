# traffic-simulator

### Requirements
- Python 3.10 or higher
- [PDM](https://pdm.fming.dev/) package manager

### Installation
- Run `pdm install` to install dependencies
- Create `config.yaml` file in the root directory
- Run `traffic-simulator` to start the simulation

## Running specific configs 

### Datamining
- `traffic-simulator --config configs/datamining_wcmp.yaml --output ./output/datamining_wcmp`
- `traffic-simulator --config configs/datamining_ecmp.yaml --output ./output/datamining_ecmp`
- `traffic-simulator --config configs/datamining_mut.yaml --output ./output/datamining_mut`
- `traffic-simulator --config configs/datamining_lc.yaml --output ./output/datamining_lc`

### ML
- `traffic-simulator --config configs/ML_wcmp.yaml --output ./output/ML_wcmp`
- `traffic-simulator --config configs/ML_ecmp.yaml --output ./output/ML_ecmp`
- `traffic-simulator --config configs/ML_mut.yaml --output ./output/ML_mut`
- `traffic-simulator --config configs/ML_lc.yaml --output ./output/ML_lc`

### Websearch
- `traffic-simulator --config configs/websearch_wcmp.yaml --output ./output/websearch_wcmp`
- `traffic-simulator --config configs/websearch_ecmp.yaml --output ./output/websearch_ecmp`
- `traffic-simulator --config configs/websearch_mut.yaml --output ./output/websearch_mut`
- `traffic-simulator --config configs/websearch_lc.yaml --output ./output/websearch_lc`

### To run with dynamically calculated lambda
- `traffic-simulator --config configs/websearch_ecmp.yaml --output ./output/websearch_ecmp_dynamic --dynamic-lambda`
