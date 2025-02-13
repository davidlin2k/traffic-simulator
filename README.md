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
- `pdm run traffic-simulator --config configs/datamining_wcmp.yaml --output ./output/datamining_wcmp`
- `pdm run traffic-simulator --config configs/datamining_ecmp.yaml --output ./output/datamining_ecmp`
- `pdm run traffic-simulator --config configs/datamining_mut.yaml --output ./output/datamining_mut`
- `pdm run traffic-simulator --config configs/datamining_lc.yaml --output ./output/datamining_lc`

### ML
- `pdm run traffic-simulator --config configs/ML_wcmp.yaml --output ./output/ML_wcmp`
- `pdm run traffic-simulator --config configs/ML_ecmp.yaml --output ./output/ML_ecmp`
- `pdm run traffic-simulator --config configs/ML_mut.yaml --output ./output/ML_mut`
- `pdm run traffic-simulator --config configs/ML_.yaml --output ./output/ML_lc`

### Websearch
- `pdm run traffic-simulator --config configs/websearch_wcmp.yaml --output ./output/websearch_wcmp`
- `pdm run traffic-simulator --config configs/websearch_ecmp.yaml --output ./output/websearch_ecmp`
- `pdm run traffic-simulator --config configs/websearch_mut.yaml --output ./output/websearch_mut`
- `pdm run traffic-simulator --config configs/websearch_lc.yaml --output ./output/websearch_lc`
  
