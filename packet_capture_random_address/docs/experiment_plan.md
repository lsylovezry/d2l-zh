# Experiment Plan: packet_capture_random_address

## 4.1 Background
- Problem definition: build a usable packet capture program plus a random address generator, then run the generator at high frequency (100000 calls/s target).
- Importance: supports network data inspection and stress-style synthetic data generation.
- Current limitation: no dedicated tool in current workspace for this specific functionality.

## 4.2 Core Hypothesis
- Key issue: ad-hoc scripts are often incomplete (no CLI, no output format, no rate control).
- Mechanism: provide modular Python tools with explicit CLI, JSONL output for packets, and rate-controlled execution loop.

## 4.3 Objectives
- Deliver runnable packet sniffer for Linux.
- Deliver random address generator supporting mixed and typed output.
- Deliver runner with configurable rate (default 100000/s) and duration.
- Measurable targets:
  - generator runner can execute with `--rate 100000`;
  - packet sniffer can capture packets and persist JSONL records.

## 4.4 Related Work
- System-level packet capture: tcpdump/libpcap family.
- Python-level alternatives: scapy/pyshark.
- This implementation is a lightweight standard-library raw socket approach.

## 4.5 Data Plan
- No offline dataset required for implementation.
- Runtime data source for sniffer: live NIC traffic from host.
- Output data:
  - `outputs/packets.jsonl` for packet summaries;
  - optional text outputs for generated addresses.

## 4.6 Task Definition
- Input:
  - sniffer: interface name, duration or packet limit;
  - generator: address type, count;
  - runner: rate, seconds, address type.
- Output:
  - sniffer: JSONL rows containing timestamp/frame/ip-level metadata;
  - generator: addresses to stdout or file;
  - runner: throughput summary.
- Supervision signal: N/A (engineering task).

## 4.7 Method Design
- Packet sniffer:
  - Use `socket.AF_PACKET + socket.SOCK_RAW`.
  - Parse Ethernet header, then IPv4/IPv6 metadata.
  - Serialize per-packet summary to JSONL.
- Random address generator:
  - IPv4/IPv6 from random bit sampling.
  - MAC with unicast + locally administered constraints.
  - URL from random lexical tokens.
- High-frequency runner:
  - Fixed-size per-second loop.
  - Best-effort pacing by sleeping for remaining second budget.

## 4.8 Implementation Plan
- Scripts:
  - `src/packet_sniffer.py`
  - `src/random_address_generator.py`
  - `scripts/run_100k_per_second.py`
- Directory structure:
  - code in `/packet_capture_random_address/src` and `/packet_capture_random_address/scripts`
  - docs in `/packet_capture_random_address/docs`
  - outputs in `/packet_capture_random_address/outputs`

## 4.9 Experiment Design
- Main checks:
  - generate sample addresses (all types);
  - run 100000/s loop for multiple seconds and inspect achieved throughput;
  - run packet sniffer for fixed duration and verify JSONL lines.
- Ablations:
  - vary `--rate` (10k, 50k, 100k, 200k);
  - vary address type cost (`ipv4` vs `mixed`).
- Failure cases:
  - no root privileges for sniffer;
  - low-end CPU cannot sustain exact 100000/s.

## 4.10 Evaluation
- Metrics:
  - achieved generation rate (calls/s);
  - total generated count;
  - captured packet count.
- Evaluation method:
  - command-line execution and output verification.

## 4.11 Risks
- Data risk: live traffic may be low on quiet interfaces.
- Training risk: N/A.
- Engineering risk:
  - raw sockets are Linux-specific and permission-gated;
  - achieved throughput may differ across hardware.

## 4.12 Resources
- Compute: CPU only.
- Storage: small text/jsonl output footprints for short runs.
- Extra: sudo/root capability for packet capture.

## 4.13 Milestones
- M1: scaffold project and docs.
- M2: implement sniffer.
- M3: implement generator and high-rate runner.
- M4: run verification commands and document usage.

## 4.14 Minimum Viable Experiment
- First runnable validation:
  - `python3 src/random_address_generator.py --count 10`
  - `python3 scripts/run_100k_per_second.py --rate 100000 --seconds 1`
  - `sudo python3 src/packet_sniffer.py --duration 2 --output outputs/packets.jsonl`
- Quick acceptance:
  - commands run without code errors;
  - outputs are produced in expected files/format.
