# AGENTS.md – Agent Guidance for BFG Fleet Simulator

### Project Purpose & Scope

This project is a browser-compatible, fully automated Python fleet battle simulator inspired by Battlefleet Gothic.
It is designed to run in Pyodide (e.g. JupyterLite/browser) using `py-rolldice` for dice mechanics and `micropip` for dependency loading.

---

### 🧠 AI Agent Behavior Guidelines

Agents operating on this repo can assume:

* Ships are autonomous; orders are random or heuristic.
* Simulation phases: order selection, hazards, shooting, missiles, boarding, repairs.
* No `input()`: all flow is deterministic/randomized.
* Use `micropip` to install packages at runtime (e.g. `await micropip.install("py-rolldice")`).

### 🧩 Architecture & Directory Layout

```
/
├── BATTLE_SIM.py       ← main simulation module
├── README.md
├── AGENTS.md
├── DESIGN_CANVAS.md    ← design documentation, flow, modular planning
└── requirements.txt
```

* Core logic in Python modules; no build pipeline.
* Design-oriented docs and spec files (`DESIGN_CANVAS.md`).
* Example notebooks or demos may exist in a `notebooks/` or `demos/` folder.

---

### ⚙️ Development & Build Tools

For local development:

* Use `pip install -r requirements.txt` or `poetry install`.
* Unit tests can be configured with `pytest`.
* All runtime dependencies (e.g. `py-rolldice`) are also installed dynamically in Pyodide via `micropip`.

Agents should also support:

* Commands for running full simulation in headless mode.
* CLI options to configure number of rounds, ships, or seed for RNG.

---

### ✅ Coding & Contribution Guidelines

* Follow consistent naming and Python style (PEP8 compatible).
* Avoid blocking I/O (especially `input()`).
* When generating `.py` files, include unterminated test cases if any.
* If writing agent-controlled test harnesses, follow the same code patterns as simulation code for modularity (e.g. classes and hooks).
* Document special systems or new orders/classes in DESIGN\_CANVAS.md for clarity.

---

### 🛠️ Testing & Verification

* Code changes must pass all simulation unit tests.
* Simulation output logs can be used for snapshot testing.
* If adding new nightmarish hazards or systems, include deterministic seed-based test data.

---

### 🤖 Agent Tools Integration Behavior

Agentic tools scanning this repo should:

* Read `AGENTS.md` from the project root as the primary instruction file.
* Prepend its content to prompts / system messages when generating code or test modules.
* Apply instructions to all files within the repo tree unless nested agent docs (none here) override.
* Use the guidance to generate code consistent with the simulator architecture and conventions.

---

### 📈 Future Expansion

Future agent-use cases may include:

* AI agent tournaments: self-playing ship controllers.
* Plug-ins for ML/RL based agents.
* Integration with REPL or visualization frontends (mermaid, web UI).
* Export battle logs or HTML report driven by agent output.

Agents should respect the modular structure and naming conventions when extending.

---

*End of AGENTS.md guidance document.*
