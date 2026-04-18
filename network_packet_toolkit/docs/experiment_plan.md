# Network Packet Toolkit Experiment Plan (v0)

## 1. Background

### Problem definition
Build a minimal but executable toolkit that combines:
1. packet capture on Linux
2. random network address generation
3. high-frequency execution at a target rate of 100000 operations per second

### Importance
This setup can be used as a lightweight systems benchmark and as a component in network simulation workloads.

### Current limitations
- Raw packet capture requires root privileges.
- Throughput is bounded by CPU performance and kernel/network conditions.
- Capturing one real packet per operation is not guaranteed because network traffic can be sparse.

## 2. Core Hypothesis

If we keep a persistent non-blocking raw socket and avoid per-iteration socket setup, we can execute the combined operation loop with a target schedule of 100000 operations per second and report achieved throughput robustly.

## 3. Objectives

1. Provide two independent modules:
   - packet sniffer
   - random address generator
2. Provide one combined runner that performs 100000 operations per second target.
3. Report runtime statistics:
   - requested ops/s
   - total operations
   - elapsed seconds
   - achieved ops/s

## 4. Related Work

- Linux raw socket capture mechanism (`AF_PACKET`, `SOCK_RAW`) as baseline systems primitive.
- Pseudo-random address generation via Python standard library (`random`, `ipaddress`) as baseline generation method.

This project is an engineering implementation task, not a novel algorithm paper.

## 5. Data Plan

No external dataset is required.
Input source is live network interface traffic from host OS.

## 6. Task Definition

### Input
- Optional network interface name (`eth0`, `ens5`, etc.)
- runtime parameters:
  - target ops/s
  - duration seconds

### Output
- packet metadata (source MAC, destination MAC, ether type) when available
- generated random endpoint (`IPv4:port`)
- aggregate throughput statistics

### Supervision signal
Not applicable (non-ML systems utility).

## 7. Method Design

1. Packet Sniffer
   - Create one raw socket with `AF_PACKET`.
   - Set non-blocking mode.
   - Poll one packet each loop; return `None` when no packet available.
2. Random Address Generator
   - Generate random IPv4/IPv6/MAC/port and endpoint with deterministic optional seed.
3. High-Frequency Runner
   - For `target_ops_per_second * duration_seconds` iterations:
     - poll sniffer once
     - generate random endpoint once
   - Measure elapsed time and compute achieved ops/s.

## 8. Implementation Plan

### Directory structure
- `src/packet_sniffer.py`
- `src/random_address_generator.py`
- `src/high_frequency_runner.py`
- `scripts/run_100k_per_second.sh`
- `README.md`

### Pipelines
- data pipeline: live packet polling
- operation pipeline: polling + generation
- evaluation pipeline: throughput metrics printout

## 9. Experiment Design

### Main experiment
- Run default script at target 100000 ops/s for 1 second.

### Baselines
- Compare with lower targets (e.g., 20000, 50000) to confirm scaling behavior.

### Ablations
- With/without interface binding
- Different duration settings

### Robustness checks
- Run when traffic is low and when traffic is high.

## 10. Evaluation

Metrics:
- achieved ops/s
- ratio: achieved / requested
- run stability over repeated launches

Method:
- parse terminal output from runner statistics.

## 11. Risks

- Permission risk: no root access → sniffer cannot open raw socket.
- Environment risk: restricted container networking may return few packets.
- Performance risk: machine may not sustain requested throughput.

## 12. Resources

- CPU-only workload.
- No dedicated GPU requirement.
- Minimal storage footprint.

## 13. Milestones

1. Implement sniffer and generator.
2. Integrate high-frequency loop.
3. Add executable script and docs.
4. Validate command-level run behavior.

## 14. Minimum Viable Experiment

Run:

```bash
sudo bash scripts/run_100k_per_second.sh
```

Expected:
- program starts successfully with root permission
- performs 100000 operations in configured duration
- prints throughput statistics
