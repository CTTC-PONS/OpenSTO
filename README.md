# OpenSTO — Open Security & Trust Orchestrator

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](#license)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#requirements)
[![Containers](https://img.shields.io/badge/Runtime-Docker%20Compose-informational.svg)](#run-with-docker-compose)

**OpenSTO** is an open-source framework for orchestrating **security & trust closed loops** in modern, multi-vendor networks.  
It automates the **collect → analyze → decide → enforce** cycle to operationalize policies and trust scores across disaggregated environments.

> **Status:** active development. Interfaces and scenarios may change between releases.

---

## Table of Contents

- [Key Features](#key-features)
- [Architecture (at a Glance)](#architecture-at-a-glance)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
  - [Run with Docker Compose](#run-with-docker-compose)
  - [Local Development (Poetry)](#local-development-poetry)
- [Minimal Scenario Walkthrough (tc4.6b)](#minimal-scenario-walkthrough-tc46b)
- [Configuration](#configuration)
- [Data & Persistence](#data--persistence)
- [Security Notes](#security-notes)
- [CLI & Library Usage](#cli--library-usage)
- [Packaging for PyPI](#packaging-for-pypi)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Key Features

- **Closed-loop Security & Trust:** codify policies and orchestrate enforcement across domains.  
- **Scenario-driven:** runnable, versioned scenarios (e.g., `tc4.6b`) for demos, tests, and research.  
- **Container-first:** one-file bring-up via `docker-compose-opensto.yml`.  
- **Python-native toolchain:** Poetry project, Ruff linting, typed-friendly codebase.  
- **Ops helpers:** `deploy.sh` / `undeploy.sh` for quick day-0/day-1 lifecycle.  

---

## Architecture (at a Glance)

```mermaid
flowchart LR
  subgraph Telemetry[Telemetry & Inputs]
    T1[Net/Host Sensors]
    T2[Logs/Events]
    T3[Inventory/CMDB]
  end

  subgraph OpenSTO
    C[Collector]
    A[Analytics & Trust Scoring]
    P[Policy Engine]
    D[Decision/Orchestration]
    E[Enforcement Adapters]
    DB[State/DB]
  end

  subgraph Targets[Targets]
    X1[Network Controllers]
    X2[Security Controls]
    X3[Cloud/K8s]
  end

  T1 --> C
  T2 --> C
  T3 --> C
  C --> A --> P --> D --> E
  E --> X1
  E --> X2
  E --> X3
  C -- state --> DB
  A -- state --> DB
  P -- policies --> DB
  D -- plans --> DB
'''

This diagram is conceptual; specific components and adapters are wired per scenario.

OpenSTO follows a modular architecture for closed-loop automation:

1. **Telemetry Collection:** gathers metrics, logs, and inventory data from network and service components.  
2. **Analytics & Trust Scoring:** evaluates data to derive insights or detect anomalies.  
3. **Policy Engine:** defines rules and trust policies driving decision-making.  
4. **Decision & Orchestration:** computes corrective actions or trust updates.  
5. **Enforcement Adapters:** apply changes to underlying systems (controllers, orchestrators, or devices).  
6. **State Database:** keeps operational state and historical data for traceability.

This loop repeats continuously to maintain a secure and trustworthy network state.

---

## Requirements

- **Docker** + **Docker Compose v2** (`docker compose` CLI)  
- **Python 3.10+** (for development / library usage)  
- **Poetry** (recommended)  
- Bash-compatible shell for helper scripts  

---

## Quick Start

### Run with Docker Compose

\`\`\`bash
git clone https://github.com/CTTC-PONS/OpenSTO.git
cd OpenSTO

# Copy an example env and adjust values as needed
cp dot_envs/example.env .env

# Bring the stack up
./deploy.sh
# or
docker compose -f docker-compose-opensto.yml up -d

# Inspect
docker compose -f docker-compose-opensto.yml ps
docker compose -f docker-compose-opensto.yml logs -f
\`\`\`

**Stop & clean:**

\`\`\`bash
./undeploy.sh
# or
docker compose -f docker-compose-opensto.yml down -v
\`\`\`

> **Ports/Endpoints:** check `docker-compose-opensto.yml` and `.env` for published ports.

---

### Local Development (Poetry)

\`\`\`bash
# 1) Install Poetry (via pipx recommended)
pipx install poetry

# 2) Install dependencies
poetry install

# 3) Activate the venv
poetry shell

# 4) Lint/format
poetry run ruff check .
poetry run ruff format .
\`\`\`

---

## Minimal Scenario Walkthrough (tc4.6b)

This repo ships with runnable scenarios under `scenarios/`.  
The example below shows a **clean run** of `tc4.6b`.

1. **Select the scenario**  
   Ensure your `.env` points to the `tc4.6b` inputs if scenario selection is controlled via environment variables.  
   If a scenario file is referenced directly in the compose stack, verify the mapped paths under `scenarios/tc4.6b/`.

2. **Deploy**

   \`\`\`bash
   docker compose -f docker-compose-opensto.yml up -d
   \`\`\`

3. **Verify Orchestrator Services**

   \`\`\`bash
   docker compose -f docker-compose-opensto.yml ps
   docker compose -f docker-compose-opensto.yml logs -f <service-name>
   \`\`\`

4. **Run the Scenario**  
   If the scenario is triggered automatically, it will start upon deployment.  
   If there is a CLI driver, run it manually (example pattern):

   \`\`\`bash
   poetry run opensto scenario run scenarios/tc4.6b
   \`\`\`

5. **Inspect Outputs**
   - Logs and artifacts under the scenario output path (often within a bound volume).  
   - Generated reports or trust scores in the configured output directory.

6. **Teardown**

   \`\`\`bash
   docker compose -f docker-compose-opensto.yml down -v
   \`\`\`

> 💡 Tip: Commit **scenario manifests** (inputs, policy snippets, expected results) to keep experiments reproducible.

---

## Configuration

- **Environment Variables:** main configuration knobs via `.env` (copy from `dot_envs/`).  
  Common items:
  - Service ports & bind addresses  
  - DB connection details & volume mounts  
  - Scenario selection and paths  
  - Security materials (certs/keys) mount paths  

- **Compose Overrides:** use `docker-compose.override.yml` for local tweaks.  
- **Secrets:** do not commit real credentials; mount via env/volumes or your secret store.

---

## Data & Persistence

- The `db/` folder and compose volumes store persistent state.  
- For a clean reset:

  \`\`\`bash
  docker compose -f docker-compose-opensto.yml down -v
  \`\`\`

---

## Security Notes

- The `security/` folder is for **development materials** (e.g., demo certs/policies).  
- Do **not** commit production keys or tokens.  
- Prefer:
  - Docker secrets / read-only mounts  
  - Env vars sourced from your secret manager  

---

## CLI & Library Usage

If you use OpenSTO as a Python library or CLI, you can structure usage like this:

### CLI

\`\`\`bash
opensto --help
opensto scenario list
opensto scenario run scenarios/tc4.6b --dry-run
\`\`\`

### Library

\`\`\`python
from opensto import Orchestrator, Scenario

sc = Scenario.from_path("scenarios/tc4.6b")
orch = Orchestrator.from_env()  # reads .env / defaults
result = orch.run(sc)
print(result.summary())
\`\`\`

> Replace `opensto`, `Orchestrator`, and `Scenario` with your actual module and class names once stabilized.

---

## Packaging for PyPI

To make the project **pip-installable** and publish to **PyPI**:

### 1. Edit `pyproject.toml`

\`\`\`toml
[project]
name = "opensto"
version = "0.1.0"
description = "Open Security & Trust Orchestrator"
authors = [{name = "CTTC PONS Team"}]
readme = "README.md"
license = {text = "Apache-2.0"}
requires-python = ">=3.10"

[project.scripts]
opensto = "opensto.cli:main"
\`\`\`

### 2. Build & Publish

\`\`\`bash
# Clean previous builds
rm -rf dist build *.egg-info

# Build
poetry build
# or
python -m build

# Upload to TestPyPI
python -m pip install --upgrade twine
twine upload --repository testpypi dist/*

# Verify install
pip install --index-url https://test.pypi.org/simple/ opensto

# Publish to PyPI
twine upload dist/*
\`\`\`

### 3. Tag your release

\`\`\`bash
git tag -a v0.1.0 -m "OpenSTO v0.1.0"
git push --tags
\`\`\`

---

## Contributing

1. Fork and create a feature branch.  
2. Run checks before opening a PR:

   \`\`\`bash
   poetry run ruff format .
   poetry run ruff check .
   \`\`\`

3. Write tests for new functionality (if applicable).  
4. Describe scenario and behavioral changes clearly in the PR.

---

## Roadmap

- Extended scenario catalog & fixtures  
- Stable northbound API (intent/policy ingestion)  
- Connectors for common controllers (Net, Sec, Cloud/K8s)  
- Hardening profiles (prod-ready images, security baselines)  
- Observability bundle (structured logs, metrics, traces)  

---

## Troubleshooting

- **Containers restart/crash**
  - `docker compose logs -f <service>` to inspect logs  
  - Check port collisions & `.env` values  

- **No scenario output**
  - Verify scenario path mapping and permissions  
  - Ensure scenario driver/entry point runs correctly  

- **Dependency issues**
  - Recreate venv:

    \`\`\`bash
    rm -rf .venv
    poetry install
    \`\`\`

---

## License

Licensed under the **Apache License 2.0**.  
See [LICENSE](LICENSE) for details.

---

## Acknowledgements

Developed by the **CTTC Packet Optical Networks & Services (PONS)** team and collaborators.  
Built to explore and operationalize **closed-loop security & trust** in open, disaggregated networks.
