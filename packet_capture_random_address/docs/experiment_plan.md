# Experiment Plan v0 - packet_capture_random_address

## 4.1 Background
- **Problem definition**: Need a practical tool combining packet capture and random address generation under strict throughput target (100k loops/s).
- **Importance**: Useful for network simulation, stress tests, and data generation pipelines.
- **Current limitations**: Typical scripts either capture packets or generate random addresses but often miss deterministic rate control.

## 4.2 Core Hypothesis
- **Key issue**: Throughput instability comes from mismatched pacing and blocking I/O.
- **Expected mechanism**: Use a lightweight per-iteration pacing controller and non-blocking-ish capture timeout to keep loop near target rate.

## 4.3 Objectives
- Hit around `100000` iterations/s in `--dry-run` mode.
- Provide real capture mode with graceful degradation depending on traffic and privilege.
- Keep implementation simple and runnable by beginners.

## 4.4 Related Work
- Linux raw socket packet capture patterns (`AF_PACKET`, `ETH_P_ALL`).
- Standard token-bucket/rate limiter pacing methods.
- Existing packet tools (tcpdump/scapy) as conceptual baseline.

## 4.5 Data Plan
- No external dataset required for v0.
- Live packet stream is data source in capture mode.
- Future extension: save packet metadata to `/outputs` as CSV/JSONL for offline analysis.

## 4.6 Task Definition
- **Input**: Runtime args (`rate`, `duration`, `iface`, `dry-run`).
- **Output**: Throughput summary and optional packet metadata event per loop.
- **Supervision signal**: Throughput proximity to target rate.

## 4.7 Method Design
- Random generator emits `{ipv4, ipv6, mac, hostname, port}`.
- Packet sniffer captures one frame metadata (`src/dst mac`, protocol, payload size).
- Runner loop does: generate -> capture (optional) -> pace.

## 4.8 Implementation Plan
- `src/.../random_address.py`: generation logic.
- `src/.../packet_capture.py`: raw socket wrapper.
- `src/.../runner.py`: command line and control loop.
- `scripts/run_100k_per_sec.sh`: reproducible launcher.

## 4.9 Experiment Design
- Main: dry-run at 100k/s for 3 sec.
- Main: capture mode at 100k/s for 3 sec on active interface.
- Ablation: lower rate (10k, 50k) to verify linear control.
- Robustness: low traffic/high traffic interface behavior.

## 4.10 Evaluation
- Primary metric: measured throughput (`iterations / elapsed`).
- Secondary: stability of elapsed time around requested duration.
- Optional: packet capture hit-rate statistics.

## 4.11 Risks
- Data risk: none in v0.
- Training risk: N/A.
- Engineering risks: raw socket permission, hardware/OS scheduling jitter.

## 4.12 Resources
- CPU-only runtime.
- Linux with root privileges for capture mode.
- Minimal disk usage.

## 4.13 Milestones
- M1: basic generator + sniffer modules.
- M2: paced runner and CLI.
- M3: verification script and usage docs.

## 4.14 Minimum Viable Experiment
- Run `./scripts/run_100k_per_sec.sh 3 --dry-run`.
- Validate throughput close to 100k/s.

## Assumptions / Missing Info
- Target interface name assumed available on host.
- Real-capture performance depends on live traffic and privileges.
