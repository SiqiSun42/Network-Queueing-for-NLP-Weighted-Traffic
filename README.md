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
- NLP-based semantic weight calculation from text corpus
- RAG-based semantic reconstruction at receiver
- End-to-end Task Success Rate evaluation

## Usage

Run single scenario:
```bash
python3 run_experiment.py
```

Run Phase 3 RAG evaluation:
```bash
python3 evaluate_rag.py
```

Run complete pipeline:
```bash
python3 run_complete_pipeline.py
```

## Project Scope

The project examines three aspects:

1. Scheduling algorithm comparison under semantic weights
2. Real-world performance with NLP-extracted packet importance
3. End-to-end semantic reconstruction quality (Task Success Rate)

## Core Files

- packet.py: Packet data structure
- traffic.py: Traffic generation with semantic weights
- maxweight_scheduler.py: Max-Weight algorithm implementation
- num_scheduler.py: NUM algorithm implementation
- network_sim.py: Simulation environment
- nlp_weight.py: Semantic weight extraction
- receiver.py: Packet reception at destination
- rag.py: Semantic reconstruction and TSR calculation
- semantic_simulator.py: End-to-end evaluation pipeline

## Evaluation Metric

Primary metric: Task Success Rate (TSR) - measures how well the reconstructed information at the receiver matches the original transmission, rather than traditional packet loss rate.
