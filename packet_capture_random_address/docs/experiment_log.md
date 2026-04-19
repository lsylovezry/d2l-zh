## Experiment Log

### Scope
- Implement packet capture utility.
- Implement random address generator.
- Implement high-frequency runner targeting 100000 iterations per second.

### Initial Validation
- Command:
  - `python3 packet_capture_random_address/scripts/run_100k_per_sec.py --seconds 1`
- Expected:
  - Program completes.
  - JSON summary printed.
  - Output file generated under `packet_capture_random_address/outputs/run_summary.json`.

### Notes
- Packet capture mode requires root privileges and a valid Linux interface.
