# Claude Code Prompt: Populate best-of-pes-ai projects.yaml

## Context
The best-of-pes-ai repo has been scaffolded using the best-of-lists/best-of template. The `projects.yaml` currently has only 3 seed projects. Your job is to replace the projects section with the full set of 40+ researched projects below, organized into 10 categories. Keep the existing `configuration`, `categories`, and `labels` sections unchanged. Only replace the `projects:` list.

## Instructions

1. Open `projects.yaml` in the best-of-pes-ai repo
2. Replace the entire `projects:` section with the entries below
3. Validate YAML syntax (no tabs, consistent indentation with 2 spaces)
4. Each project entry uses this schema:

```yaml
- name: "Display Name"
  github_id: "owner/repo"
  category: "category-key"
  labels: ["python", "pytorch"]  # from defined labels
  description: "One-line description of AI/ML relevance to power systems."
  pypi_id: "package-name"        # optional, only if on PyPI
  conda_id: "conda-forge/name"   # optional, only if on conda-forge
  homepage: "https://..."         # optional
```

## Projects to Add

### Category: load-forecasting

```yaml
  - name: "OpenSTEF"
    github_id: "OpenSTEF/openstef"
    category: "load-forecasting"
    labels: ["python"]
    description: "Automated ML pipelines for short-term energy forecasting. LF Energy project from Dutch DSO Alliander."
    pypi_id: "openstef"
    homepage: "https://www.lfenergy.org/projects/openstef/"

  - name: "LSTM Load Forecasting"
    github_id: "dafrie/lstm-load-forecasting"
    category: "load-forecasting"
    labels: ["python", "jupyter"]
    description: "LSTM-based load forecasting with TBATS and ARIMA benchmarks. Swiss grid data."

  - name: "Short-Term Load Forecasting"
    github_id: "sarajcev/STLF"
    category: "load-forecasting"
    labels: ["python", "jupyter"]
    description: "Substation-level short-term load forecasting using stacking ensemble. Ausgrid data."

  - name: "Electric Generation Forecasting"
    github_id: "Helmholtz-AI-Energy/electric-generation-forecasting"
    category: "load-forecasting"
    labels: ["python", "pytorch"]
    description: "LSTM-CNN models for German electricity generation mix forecasting."
```

### Category: grid-optimization

```yaml
  - name: "pandapower"
    github_id: "e2nIEE/pandapower"
    category: "grid-optimization"
    labels: ["python", "jupyter"]
    description: "Power system modeling and analysis. Pandas-based, PYPOWER compatible. Univ. Kassel + Fraunhofer IEE."
    pypi_id: "pandapower"
    conda_id: "conda-forge/pandapower"
    homepage: "https://www.pandapower.org/"

  - name: "Power Grid Model"
    github_id: "PowerGridModel/power-grid-model"
    category: "grid-optimization"
    labels: ["python"]
    description: "High-performance C++/Python distribution grid calculations. LF Energy project. Power flow and state estimation."
    pypi_id: "power-grid-model"
    conda_id: "conda-forge/power-grid-model"

  - name: "PyPSA"
    github_id: "PyPSA/PyPSA"
    category: "grid-optimization"
    labels: ["python", "jupyter"]
    description: "Python for Power System Analysis - optimization and simulation of modern power systems."
    pypi_id: "pypsa"
    conda_id: "conda-forge/pypsa"
    homepage: "https://pypsa.org"

  - name: "PyPSA-USA"
    github_id: "PyPSA/pypsa-usa"
    category: "grid-optimization"
    labels: ["python", "jupyter", "university"]
    description: "Open-source power systems model of US bulk transmission. Capacity expansion and production cost simulation."
    homepage: "https://pypsa.org"

  - name: "PyPSA-Earth"
    github_id: "pypsa-meets-earth/pypsa-earth"
    category: "grid-optimization"
    labels: ["python"]
    description: "First open-source global cross-sectoral energy system model with high spatial/temporal resolution."
    homepage: "https://pypsa-meets-earth.github.io/"

  - name: "GNN Optimal Power Flow"
    github_id: "ShaohuiLiu/GNN_OPF_electricity_market"
    category: "grid-optimization"
    labels: ["python", "pytorch"]
    description: "Topology-informed GNN for AC-OPF and LMP prediction. Published in IEEE TPWRS."

  - name: "GNN Power Flow"
    github_id: "mukhlishga/gnn-powerflow"
    category: "grid-optimization"
    labels: ["python", "pytorch"]
    description: "Graph neural networks for AC power flow prediction using PyTorch Geometric."
```

### Category: renewable-forecasting

```yaml
  - name: "Power Predictor"
    github_id: "SverreNyworken/power-predictor"
    category: "renewable-forecasting"
    labels: ["python"]
    description: "ML-based solar and wind power generation prediction."

  - name: "Austin Green Energy Predictor"
    github_id: "Duvey314/austin-green-energy-predictor"
    category: "renewable-forecasting"
    labels: ["python", "jupyter"]
    description: "Wind and solar energy prediction for Austin, Texas using ML models."

  - name: "Atlite"
    github_id: "PyPSA/atlite"
    category: "renewable-forecasting"
    labels: ["python"]
    description: "Calculating renewable power potentials from weather data. Part of PyPSA ecosystem."
    pypi_id: "atlite"
    conda_id: "conda-forge/atlite"

  - name: "PowerGenome"
    github_id: "PowerGenome/PowerGenome"
    category: "renewable-forecasting"
    labels: ["python"]
    description: "Create inputs for power systems models including renewable generation profiles."
    pypi_id: "PowerGenome"
    homepage: "https://github.com/PowerGenome/PowerGenome"
```

### Category: fault-detection

```yaml
  - name: "PyOD"
    github_id: "yzhao062/pyod"
    category: "fault-detection"
    labels: ["python"]
    description: "50+ anomaly detection algorithms. 26M+ downloads. Widely used for grid anomaly detection."
    pypi_id: "pyod"
    conda_id: "conda-forge/pyod"
    homepage: "https://pyod.readthedocs.io/"

  - name: "Powerline Fault Detection"
    github_id: "oneapi-src/powerline-fault-detection"
    category: "fault-detection"
    labels: ["python"]
    description: "Intel-optimized partial discharge detection using Random Forest. Power line diagnostics."

  - name: "Power Laws Anomalies"
    github_id: "drivendataorg/power-laws-anomalies"
    category: "fault-detection"
    labels: ["python", "jupyter"]
    description: "Competition winning code for building energy anomaly detection. DrivenData challenge."

  - name: "Power System Anomaly Identification"
    github_id: "mile888/anomaly_identification"
    category: "fault-detection"
    labels: ["python"]
    description: "WLS-EKF state estimation combined with ML for power system anomaly detection."

  - name: "Microgrid Fault Detection"
    github_id: "AgHarsh/Fault-Detection-in-Power-Microgrid"
    category: "fault-detection"
    labels: ["python"]
    description: "ANN-based fault detection and location in power microgrids."
```

### Category: grid-stability

```yaml
  - name: "Grid2Op"
    github_id: "Grid2op/grid2op"
    category: "grid-stability"
    labels: ["python", "jupyter"]
    description: "RL testbed for power grid operations. RTE France. L2RPN competitions. Gymnasium-compatible."
    pypi_id: "grid2op"
    homepage: "https://l2rpn.chalearn.org/"

  - name: "RL2Grid"
    github_id: "emarche/RL2Grid"
    category: "grid-stability"
    labels: ["python"]
    description: "RL benchmark for power grid operations. Built on Grid2Op. RTE/50Hertz/National Grid ESO/MIT collab."

  - name: "LightSim2Grid"
    github_id: "Grid2op/lightsim2grid"
    category: "grid-stability"
    labels: ["python"]
    description: "Fast C++ backend for Grid2Op power flow computations. MPL-2.0 license."
    pypi_id: "LightSim2Grid"

  - name: "Chronix2Grid"
    github_id: "Grid2op/chronix2grid"
    category: "grid-stability"
    labels: ["python"]
    description: "Synthetic time series generation for Grid2Op environments. Load and renewable profiles."
    pypi_id: "chronix2grid"

  - name: "L2RPN Baselines"
    github_id: "Grid2op/l2rpn-baselines"
    category: "grid-stability"
    labels: ["python", "pytorch"]
    description: "Baseline RL agents for L2RPN power grid competitions. Reference implementations."
    pypi_id: "l2rpn-baselines"
```

### Category: der-management

```yaml
  - name: "pymgrid"
    github_id: "Total-RD/pymgrid"
    category: "der-management"
    labels: ["python"]
    description: "Python microgrid simulator with 25 pre-packaged benchmarks. RL-compatible."
    pypi_id: "pymgrid"

  - name: "OpenModelica Microgrid Gym"
    github_id: "upb-lea/openmodelica-microgrid-gym"
    category: "der-management"
    labels: ["python"]
    description: "OpenAI Gym environment for microgrid control using RL. FMI standard compatible."
    pypi_id: "openmodelica-microgrid-gym"

  - name: "DRL Microgrid Energy Management"
    github_id: "tahanakabi/DRL-for-microgrid-energy-management"
    category: "der-management"
    labels: ["python"]
    description: "Deep RL for microgrid energy management systems. 7 DRL algorithms compared."

  - name: "Microgrid EMS DRL"
    github_id: "GitX123/microgrid-ems-drl"
    category: "der-management"
    labels: ["python"]
    description: "Deep RL for battery management in microgrids with time series observation."
```

### Category: nlp-standards

```yaml
  - name: "Talk2PowerSystem"
    github_id: "statnett/Talk2PowerSystem"
    category: "nlp-standards"
    labels: ["python"]
    description: "Natural language interface for querying CIM-based power system models. Norwegian TSO Statnett."
    homepage: "https://github.com/statnett/Talk2PowerSystem"

  - name: "PyPSA MCP"
    github_id: "PyPSA/pypsa-mcp"
    category: "nlp-standards"
    labels: ["python"]
    description: "PyPSA energy modeling for LLMs via Model Context Protocol. Natural language grid analysis."
```

### Category: synthetic-data

```yaml
  - name: "PGLib-OPF"
    github_id: "power-grid-lib/pglib-opf"
    category: "synthetic-data"
    labels: []
    description: "Benchmark library for optimal power flow. IEEE test cases and realistic networks."
    homepage: "https://power-grid-lib.github.io/"

  - name: "PGLib-UC"
    github_id: "power-grid-lib/pglib-uc"
    category: "synthetic-data"
    labels: []
    description: "Benchmark library for unit commitment problems. Standard test instances."

  - name: "GridStatus"
    github_id: "gridstatus/gridstatus"
    category: "synthetic-data"
    labels: ["python"]
    description: "Uniform API for US/Canada ISO electricity data. CAISO, ERCOT, PJM, MISO, NYISO, SPP, ISONE."
    pypi_id: "gridstatus"
    homepage: "https://www.gridstatus.io/"

  - name: "SimBench"
    github_id: "e2nIEE/simbench"
    category: "synthetic-data"
    labels: ["python", "jupyter"]
    description: "Benchmark dataset of German LV/MV/HV grids for power system analysis."
    pypi_id: "simbench"

  - name: "HELICS"
    github_id: "GMLC-TDC/HELICS"
    category: "synthetic-data"
    labels: ["python"]
    description: "Co-simulation framework for energy systems. NREL/LLNL/PNNL/ANL collaboration."
    pypi_id: "helics"
    homepage: "https://helics.org/"
```

### Category: computer-vision

```yaml
  - name: "InsPLAD"
    github_id: "andreluizbvs/InsPLAD"
    category: "computer-vision"
    labels: ["python", "pytorch"]
    description: "Power Line Asset Inspection Dataset. 10,607 UAV images, 17 asset types, 6 defect types. IJRS published."

  - name: "Grid2Viz"
    github_id: "Grid2op/grid2viz"
    category: "computer-vision"
    labels: ["python"]
    description: "Visualization tool for Grid2Op power grid environments. Agent behavior analysis."
    pypi_id: "grid2viz"
```

### Category: energy-markets

```yaml
  - name: "GNN OPF Electricity Market"
    github_id: "ShaohuiLiu/GNN_OPF_electricity_market"
    category: "energy-markets"
    labels: ["python", "pytorch"]
    description: "GNN for AC-OPF and locational marginal price prediction. IEEE TPWRS published."

  - name: "Electricity Price Prediction"
    github_id: "Carterbouley/ElectricityPricePrediction"
    category: "energy-markets"
    labels: ["python", "jupyter"]
    description: "Neural networks for day-ahead electricity price forecasting. Nordpool market data."

  - name: "AMES Market"
    github_id: "ames-market/AMES-V5.0"
    category: "energy-markets"
    labels: ["python"]
    description: "Agent-based wholesale power market test bed. Iowa State University."
    homepage: "https://www2.econ.iastate.edu/tesfatsi/AMESMarketHome.htm"
```

## After updating projects.yaml

1. Run `python -c "import yaml; yaml.safe_load(open('projects.yaml'))"` to validate syntax
2. Count total projects and confirm 40+ entries
3. Verify each category has at least 2 projects
4. Check no duplicate github_id entries
5. Ensure all category keys match the categories defined in the configuration section

## Notes
- Some projects appear in two categories (e.g., GNN_OPF appears in both grid-optimization and energy-markets). The best-of generator handles this fine — the project shows up in both sections. But if you'd prefer no duplicates, keep it only in the primary category (grid-optimization for GNN_OPF).
- The `labels` field only uses labels defined in the `labels:` section of projects.yaml. Currently defined: python, julia, jupyter, tensorflow, pytorch, university, national-lab. Don't use labels not in that list.
- pypi_id should be the exact PyPI package name (what you'd `pip install`). Only include if confirmed.
- Star counts as of Feb 2026 research: pandapower ~1.1K, PyPSA ~1.8K, Grid2Op ~410, GridStatus ~380, PGLib-OPF ~380, PyOD ~9K+, Power Grid Model ~210, OpenSTEF ~117, HELICS ~160
