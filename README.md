# Network Queueing for NLP-Weighted Traffic

## Project Overview

This project compares two network scheduling algorithms for handling semantic communication traffic where packets have varying importance levels based on their semantic content.

## Background and Motivation

Traditional network queues treat all packets equally. When congestion occurs, routers drop packets indiscriminately. However, in semantic communication systems, different packets carry different semantic importance. For example, a core action verb in a message is more important than a modifier.

This project explores how to allocate network resources under bandwidth constraints to maximize the semantic utility of transmitted information, not just raw throughput.

## Main Problem

Given bursts of traffic arriving at a bottleneck link, with each packet assigned a semantic importance weight, how should a scheduler decide which packets to transmit and which to drop?

## Approaches

The project compares two scheduling algorithms:

1. NUM (Network Utility Maximization): Formulates the problem as a convex optimization, computing optimal static rate allocation based on packet weights.

2. Max-Weight Scheduling (Lyapunov-based): Uses dynamic, real-time decisions. Each time slot, the scheduler prioritizes packets based on queue backlog length times packet weight. This adapts to traffic variations.

## Implementation

- Lightweight Python simulation framework
- Packet-level discrete-time simulator
- Poisson traffic generation with configurable weight distributions
- Two complete scheduler implementations
- NLP-based semantic weight extraction from a text corpus (`nlp_weight.py`); under **semantic** traffic, each packet’s **payload** carries the corresponding text **segment** (`traffic.py`) so the receiver can aggregate real tokens, not only symbolic IDs
- Receiver joins **delivered** packet payloads in **`packet_id`** order (`receiver.py`)
- **`rag.py`** supplies **`weighted_similarity`** / **`TaskSuccessRateCalculator.calculate_tsr`**, used as the **Task Success Rate (TSR)** when comparing corpus lines to the aggregate delivered text
- **`semantic_simulator.py`**: end-to-end Phase 3 evaluation — **one shared arrival trace per scenario** is replayed for Max-Weight and NUM so comparisons are fair; TSR is computed **directly** from delivered aggregate text (see **Evaluation Metric**)
- Optional **`RAGReconstructor`** (still in `rag.py`) can be used for retrieval-style reconstruction experiments; the default **`evaluate_rag.py`** pipeline follows the **direct aggregate–vs–corpus-line** TSR definition below

## Usage

Run single scenario:

```bash
python3 run_experiment.py
```

Run Phase 3 end-to-end semantic evaluation (script name `evaluate_rag.py`; metrics are TSR on delivered text, not legacy RAG-only reconstruction):

```bash
python3 evaluate_rag.py
```

This writes outputs under `slides_images/`:

- `tsr_evaluation_results.json` — per-scenario parameters, per-scheduler averages, per–corpus-line TSR samples, drops
- `tsr_evaluation_summary.txt` — short text summary
- `tsr_average_by_scenario.png` — grouped bar chart (Max-Weight vs NUM) with numeric labels

Run complete pipeline:

```bash
python3 run_complete_pipeline.py
```

## Project Scope

The project examines three aspects:

1. Scheduling algorithm comparison under semantic weights
2. Behavior under NLP-derived packet importance (semantic weight distribution)
3. End-to-end **Task Success Rate**: similarity between selected **original corpus lines** and the **concatenation of successfully delivered packet payloads**, under controlled paired traffic

## Core Files

- `packet.py`: Packet data structure (`packet_id`, `weight`, `content`, `arrival_time`, …)
- `traffic.py`: Poisson arrivals; **semantic** mode draws weights and **segment text** from the corpus-derived pool
- `maxweight_scheduler.py`: Max-Weight scheduler
- `num_scheduler.py`: NUM scheduler
- `network_sim.py`: Core scheduling comparison simulator (throughput, queues, loss); figures such as weighted throughput vs offered load use **slot-level semantic sums**, not end-to-end TSR (see plot footnotes / JSON `y_axis` fields)
- `nlp_weight.py`: Token / segment weighting from corpus text
- `receiver.py`: Stores delivered packets; **`get_received_content()`** sorts by **`packet_id`** and joins **`content`**
- `rag.py`: **`weighted_similarity`**, **`TaskSuccessRateCalculator`**, and optional **`RAGReconstructor`**
- `semantic_simulator.py`: Phase 3 simulator — shared arrival trace, delivery to receiver, TSR and semantic-preservation statistics
- `evaluate_rag.py`: Runs bundled scenarios and exports JSON / TXT / PNG under `slides_images/`

## Evaluation Metric

### Task Success Rate (TSR) — Phase 3 (`evaluate_rag.py` / `semantic_simulator.py`)

**Definition (implemented):** For each of the **first three lines** of `corpus.txt` (when present), TSR is

`TaskSuccessRateCalculator.calculate_tsr(original_line, received_aggregate)`

which wraps **`weighted_similarity`** in `rag.py` (weighted precision/recall–style score over token sets, capped/scaled as implemented there).

**`received_aggregate`** is the string obtained by sorting **delivered** packets by **`packet_id`** and joining their **`content`** fields. Under **semantic** traffic, payloads are **short NLP segments**, so this string carries tokens that can overlap each corpus line in a scheduler-dependent way.

**Fair comparison:** For each scenario, the simulator builds **one** per-slot arrival trace and **replays** it for Max-Weight and then for NUM (**same arrivals**, different scheduling).

**Semantic preservation (reported alongside TSR):** For each corpus line, intersection size of token sets \(|\text{tokens}(\text{original}) \cap \text{tokens}(\text{received_aggregate})|\) divided by \(|\text{tokens}(\text{original})|\).

**Not TSR:** Queue-length plots, congestion sweeps, and “weighted throughput vs λ/C” charts summarize **queueing / forwarded semantic mass per slot** (see respective scripts and JSON descriptions). They do **not** use the Phase 3 TSR definition unless explicitly stated.

### Traditional metrics

Packet counts, drops, and unweighted / weighted loss rates remain available via `network_sim.py` and related scripts for scheduling-layer analysis.
