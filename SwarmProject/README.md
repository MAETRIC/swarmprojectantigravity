# SWED-A — Swarm Edge Defence for Air-Gapped Networks

## Overview
SWED-A is a novel, decentralized, swarm-based intrusion detection and autonomous containment system explicitly designed for air-gapped cyber-physical environments (such as military lab setups, ICS/SCADA systems, and specialized research institutions). 

By leveraging lightweight machine learning models (Isolation Forests) distributed across multiple edge nodes, SWED-A continuously monitors network traffic, detects zero-day anomalies, validates threats through a peer-to-peer swarm consensus mechanism, and isolates compromised assets autonomously — requiring zero internet connectivity or centralized control.

## Key Features & Novelty
1. **Decentralized Swarm Intelligence**: Removes the single point of failure inherent in centralized controllers by employing a fully peer-to-peer voting consensus mechanism.
2. **Edge Machine Learning**: Implements lightweight anomaly detection (Isolation Forests) suitable for Raspberry Pi class hardware.
3. **Autonomous Containment**: Executes immediate isolation of components flagged by the swarm to prevent propagation.
4. **Air-Gap Focused**: Runs entirely localized without cloud dependencies.
5. **Multi-Vector Threat Detection**: Designed to identify varying CPS attacks including DoS, False Data Injection (FDI), and Lateral Movement.

## Architecture
The framework consists of 5 core layers:
1. **CPS Environment Layer**: Simulated cyber-physical devices and sensors.
2. **Edge Sensing Layer**: Multiple lightweight edge agents capturing telemetry.
3. **Feature Engineering Layer**: Extraction of contextual behavior (packet rates, unique port distributions, burst scores).
4. **Local Anomaly Detection**: Unsupervised learning via `IsolationForest` on each node.
5. **Swarm Consensus & Containment Layer**: Majority voting scheme dictating isolation rules.

## Academic Context & Research Alignment
This architectural prototype draws inspiration from contemporary cyber-defense literature:
- *Distributed IDS* (Mohan et al., 2020) — Distributed monitoring for SCADA grids.
- *Consensus-based detection* (Pedroso et al., 2020) — Leveraging voting in FDI IoT scenarios.
- *Edge ML deployment* (Singh et al., 2019) — Edge-centric computation optimizations.
- *Multi-agent coordination* (Alqithami, 2023) — Applying reinforcement/agent paradigms to IDS.
- *Decentralized swarm security* (Singh & Roy, 2023) - DMAS algorithms.
- *Air-gap vulnerability context* (Guri, 2020) — Understanding modern threats traversing air-gaps.

## Installation & Setup
1. Ensure Python 3.12 is installed.
2. Clone/download the project.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulation
```bash
python main.py
```

### What Happens During Simulation:
1. **Model Training**: Baseline normal behavior is generated and models are trained on all nodes.
2. **Normal Monitoring**: Live samples are evaluated, confirming standard traffic.
3. **Attack Injection**: Three attack profiles (DoS, FDI, Lateral Movement) are introduced sequentially.
4. **Consensus & Containment**: The nodes agree on anomalous behavior, log the incident, and execute a simulated device containment.
5. **Network Visualization**: Generates a dynamic layout saved as `network_state.png`.
