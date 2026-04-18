# Packet Sniffer + Random Address Generator Plan (v0)

## 1. Background
- Goal: implement a Linux packet sniffer and a random address generator.
- Performance target: support 100000 generations per second for random addresses.
- Constraint: no existing module in this repository, so new scripts and docs are required.

## 2. Core Hypothesis
- Python standard library (`socket` + `random` + batch generation) is enough for a usable sniffer and a 100k/s generator.
- A fixed one-second window with batch generation can keep throughput near the target.

## 3. Objectives
- O1: deliver runnable sniffer `src/packet_sniffer.py`.
- O2: deliver random generator `src/random_address_generator.py` with default 100000/s target.
- O3: provide one-command launcher `scripts/run_100k_per_sec.sh`.
- O4: provide clear permission and run instructions (`raw socket` needs root).

## 4. Related Work
- Engineering baseline: Linux AF_PACKET raw socket sniffing.
- Generation baseline: 32-bit pseudo-random value mapped to dotted IPv4.

## 5. Data Plan
- No offline dataset needed.
- Sniffer data source is live local network traffic.

## 6. Task Definition
- Input:
  - Sniffer: interface, count, timeout, protocol filter.
  - Generator: address type, rate, duration, batch size.
- Output:
  - Sniffer JSONL events.
  - Generated address text output (optional) and throughput stats.

## 7. Method Design
- Sniffer:
  - Open raw socket and read Ethernet frames.
  - Parse IPv4 header and basic TCP/UDP/ICMP fields.
  - Filter and emit JSON events.
- Generator:
  - Use `getrandbits` with batch mode.
  - Control target rate with one-second window.
  - Print generated total and achieved rate.

## 8. Implementation Plan
- `src/packet_sniffer.py`: packet capture core logic.
- `src/random_address_generator.py`: high-throughput address generation.
- `scripts/run_100k_per_sec.sh`: one-command 100000/s run.
- `README.md`: usage and examples.

## 9. Experiment Design
- E1: run generator for 3s and verify `achieved_rate` is near 100000/s.
- E2: capture a few packets and verify required fields and protocol filter.

## 10. Evaluation
- Generator metric: `achieved_rate`.
- Sniffer metrics: captured count, parseable JSON, protocol filter behavior.

## 11. Risks
- Raw socket requires root; without root sniffing fails.
- Low network traffic can cause fewer captured packets before timeout.

## 12. Resources
- CPU: standard single machine is enough.
- Storage: only logs and output files.

## 13. Milestones
- M1: create project structure.
- M2: finish both core programs.
- M3: finish scripts and docs.
- M4: run validation and commit.

## 14. Minimum Viable Experiment
- Command:
  - `bash scripts/run_100k_per_sec.sh`
- Expected:
  - stderr prints `achieved_rate` near 100000/s.
