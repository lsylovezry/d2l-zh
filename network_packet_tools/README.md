# Network Packet Tools

This project contains:

1. A packet sniffer (`src/packet_sniffer.py`)
2. A random address generator (`src/random_address_generator.py`)
3. A high-frequency runner that executes generation at `100000` times per second by default (`src/run_100k_per_sec.py`)

## Quick Start

```bash
cd /workspace/network_packet_tools
python3 src/random_address_generator.py --type ipv4 --count 5
python3 src/run_100k_per_sec.py --rate 100000 --duration 3 --type ipv4
```

### Packet Sniffer (Linux)

Raw socket sniffing usually requires root privileges.

```bash
sudo python3 src/packet_sniffer.py --interface eth0 --count 20
```

Save output to JSONL:

```bash
sudo python3 src/packet_sniffer.py --interface eth0 --count 20 --output outputs/capture.jsonl
```

## Notes

- The sniffer is for legitimate local network diagnostics and learning.
- `run_100k_per_sec.py` defaults to 100000 executions per second and reports per-second statistics.
