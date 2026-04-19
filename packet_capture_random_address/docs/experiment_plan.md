# Experiment Plan (v0)

## Assumptions and missing information

- The required template file `/moban.md` is not present in this repository at the time of writing.
- This plan follows the mandatory section structure from the workflow rules as a v0 executable plan.
- Scope is limited to Linux runtime where raw sockets are available.

## 4.1 Background

- **Problem definition**: Build a practical toolset with two core functions:
  1) packet capture from a Linux network interface, and 2) random network address generation.
- **Importance**: Useful for network simulation, traffic metadata sampling, stress-testing data pipelines, and synthetic endpoint generation.
- **Current limitations**:
  - Raw packet capture generally requires root privileges.
  - Python timer precision and scheduling jitter limit exact per-second pacing at very high loop rates.
  - Single-threaded generation may not reach exactly 100000 effective iterations/sec on all machines.

## 4.2 Core Hypothesis

- **Key issue**: A naive loop cannot reliably enforce high-frequency execution cadence with reproducible runtime telemetry.
- **Expected improvement mechanism**:
  - Use deterministic target-interval pacing (`interval = 1 / target_rate`).
  - Emit JSON summary with achieved throughput and elapsed time.
  - Keep packet capture optional and parallel to avoid coupling capture latency into the generation loop.

## 4.3 Objectives

- Implement runnable scripts for:
  - packet capture
  - random address generation
  - 100000 iterations/sec runner
- Measurable targets:
  - Produce exactly `target_rate * seconds` iterations in logical loop count.
  - Report achieved rate and runtime in machine-readable JSON.
  - Capture metadata records when capture mode is enabled.

## 4.4 Related Work

- **Baseline paradigm A**: Linux `AF_PACKET` raw socket capture.
- **Baseline paradigm B**: Synthetic address generation with random IPv4/IPv6/MAC/port fields.
- **Relation to this project**:
  - Not proposing a novel algorithmic contribution.
  - Contribution is engineering integration and reproducible execution wrapper.

## 4.5 Data Plan

- No external dataset is required.
- Data sources are runtime-generated:
  - Random address records (`generate_address_record`)
  - Captured packet metadata (`timestamp`, `packet_length`, `interface`, `eth_type`)
- Output storage:
  - Summary JSON in `/packet_capture_random_address/outputs`
  - Optional captured metadata JSON from packet capture script
- Preprocessing/splits/augmentation: not applicable.

## 4.6 Task Definition

- **Input format**:
  - CLI arguments (`--seconds`, `--iterations-per-second`, `--enable-capture`, `--interface`, etc.)
- **Output format**:
  - JSON printed to stdout and written to output file
- **Supervision signal**:
  - Not a learning task; correctness defined by runtime behavior and output integrity.

## 4.7 Method Design

- **Pipeline**:
  1) Parse CLI args.
  2) Optionally start background capture thread.
  3) Run fixed-rate generation loop.
  4) Aggregate summary and save to JSON.
- **Model structure**: none (non-ML utility).
- **Training paradigm**: none.
- **Inference behavior**: deterministic control flow with random sample generation each iteration.

## 4.8 Implementation Plan

- Required scripts:
  - `scripts/random_address_generator.py`
  - `scripts/packet_capture.py`
  - `scripts/run_100k_per_sec.py`
- Required modules:
  - `src/random_address_generator.py`
  - `src/packet_capture.py`
- Data pipeline:
  - Generate/capture runtime records -> serialize JSON.
- Evaluation pipeline:
  - Run scripts with controlled args and inspect summary outputs.

## 4.9 Experiment Design

- **Main experiments**:
  - Run 100k loop for 1 second and 3 seconds; compare achieved rates.
- **Baselines**:
  - Same loop without sleep pacing (max-throughput baseline).
  - Pacing with and without capture thread.
- **Ablations**:
  - Different target rates (10k, 50k, 100k, 200k).
  - Different capture max packet values.
- **Robustness**:
  - Different interfaces and host loads.
- **Failure cases**:
  - Permission denied on raw socket.
  - Non-existent interface.

## 4.10 Evaluation

- Metrics:
  - target iterations/sec
  - achieved iterations/sec
  - elapsed runtime
  - captured packet count (when enabled)
- Evaluation method:
  - CLI smoke tests + JSON output verification.
- Human eval: not required.

## 4.11 Risks

- **Data risks**: none (synthetic runtime data).
- **Training risks**: not applicable.
- **Engineering risks**:
  - High CPU usage at target rate.
  - Clock jitter causing achieved rate below target.
  - Privilege issues for packet capture.

## 4.12 Resources

- GPU needs: none.
- Runtime needs:
  - Linux host, Python 3.
  - Root privileges for capture mode.
- Storage needs:
  - Minimal (small JSON outputs by default).

## 4.13 Milestones

- M1: Create project structure and baseline scripts.
- M2: Implement address generator + packet capture modules.
- M3: Integrate 100k/sec runner and JSON reporting.
- M4: Validate execution and document usage.

## 4.14 Minimum Viable Experiment

- First runnable command:
  - `python3 packet_capture_random_address/scripts/run_100k_per_sec.py --seconds 1`
- Quick validation strategy:
  - Check process exits normally.
  - Confirm `total_iterations == 100000`.
  - Confirm summary JSON exists under `outputs/`.
