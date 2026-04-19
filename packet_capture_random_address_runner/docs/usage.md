# Usage Guide

## Purpose

This project provides:

1. A packet sniffer for Linux raw sockets.
2. A random address generator (IPv4, IPv6, MAC).
3. A high-rate runner targeting 100000 generations per second.

## Commands

### Generation only

```bash
python scripts/run.py --mode generate-only --rate 100000 --duration 2
```

### Packet sniff + generation

```bash
sudo python scripts/run.py --mode sniff-and-generate --interface eth0 --rate 100000 --duration 3 --sample-packets 5
```

## Output

The script prints a JSON report including:

- target rate
- actual achieved rate
- total generated count
- random sample output
- packet samples (sniff mode)

## Notes

- Raw packet sniffing usually requires root privileges.
- Achieved rate depends on CPU and runtime overhead.
- Use only in authorized and legal environments.
