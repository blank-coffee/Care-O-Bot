# Care-O-Bot LTL Miner

## Overview

The Care-O-Bot LTL Miner is a Python-based property mining framework that generates, verifies, and analyzes Linear Temporal Logic (LTL) properties from execution traces of a Promela model.

The system uses SPIN-generated traces to identify observable propositions, construct candidate temporal properties, and verify those candidates against the complete model using model checking. Verified properties are categorized, scored, and recorded for later analysis.

The framework supports:

- Trace generation using SPIN
- Candidate LTL property generation
- Property verification through model checking
- Property classification
  - Safety
  - Liveness
  - Response
  - Fairness
- Verification result caching
- Statistics collection
- Graph-based analysis of mining results

---

## Directory Structure

```text
Care-O-Bot
│
├── game
│   ├── game_state.py
│   ├── gui.py
│   ├── player_session.py
│   ├── replay.py
│   ├── scoring.py
│   └── statistics.py
│
├── miner
│   ├── formula_generator.py
│   ├── formula_validator.py
│   ├── miner_engine.py
│   ├── trace_parser.py
│   ├── trace_runner.py
│   └── verifier.py
│
├── promela
│   └── CareBot.pml
│
├── results
│   ├── cache
│   │   └── verifier_cache.json
│   ├── logs
│   └── stats
│
├── main.py
├── README.md
└── .gitignore
```

---

## Requirements

### Python

Tested with:

```text
Python 3.14
```

### SPIN

SPIN must be installed and accessible through WSL.

Verify installation:

```bash
spin -V
```

### GCC

Used to compile SPIN verification artifacts.

Verify installation:

```bash
gcc --version
```

### WSL

The miner currently invokes SPIN and GCC through WSL.

Verify:

```powershell
wsl --status
```

---

## Python Dependencies

Install required packages:

```powershell
pip install matplotlib numpy
```

---

## Running the Miner

Launch the application:

```pycharm
is what I'd reccomend, any ide is fine
```


---

## Mining Pipeline

The mining process follows the workflow below:

```text
Promela Model
        ↓
     SPIN Trace
        ↓
 Trace Parsing
        ↓
 Proposition Extraction
        ↓
 Candidate Generation
        ↓
 Model Checking Verification
        ↓
 Verified Properties
        ↓
 Statistics & Analysis
```

---

## Candidate Property Types

The miner generates multiple classes of temporal properties.

### Liveness

```text
<> p
```

Examples:

```text
<> charging
<> task_completed
```

---

### Safety

```text
[] p
```

Examples:

```text
[] charging
[] task_active
```

---

### Response

```text
[] (p -> <> q)
```

Examples:

```text
[] (low_battery -> <> charging)

[] (task_active -> <> task_completed)
```

---

### Fairness

```text
[] <> p
```

Examples:

```text
[] <> charging

[] <> task_active
```

---

## Verification Cache

Verified properties are cached to avoid repeated model-checking operations.

Cache location:

```text
results/cache/verifier_cache.json
```

The cache is intentionally preserved between executions.

---

## Statistics Collection

When enabled, each execution records summary statistics including:

- Winner
- Human score
- Miner score
- Verified properties
- Candidate counts
- Property classifications

Statistics are stored in:

```text
results/stats
```

---

## Available Graphs

### Score Progression

Displays human and miner scores across runs.

Purpose:

```text
Human Score vs Miner Score
over time
```

---

### Property Classification

Displays verified property categories discovered by both mining strategies.

Categories:

```text
Safety
Liveness
Response
Fairness
```

---

## Generated Data

Generated runtime artifacts:

```text
results/logs
results/stats
```

may be safely deleted.

Verification cache:

```text
results/cache/verifier_cache.json
```

should generally be retained.

---

## Notes

- The miner operates on observable propositions extracted from SPIN execution traces.
- Candidate properties are validated against the complete model using SPIN model checking.
- Verification results may vary if the Promela model is modified.
- Larger models can significantly increase verification time and candidate generation space.

---

