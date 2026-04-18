# packet_capture_random_address

Two tools:

1. `src/packet_sniffer.py`: Linux raw-socket packet sniffer, writes JSONL packet summaries.
2. `src/random_address_generator.py`: Random address generator (IPv4/IPv6/MAC/URL).

And one high-frequency runner:

- `scripts/run_100k_per_second.py`: Run generator at target calls per second (default 100000/s).
- `scripts/run_capture_and_generate.py`: Start capture and 100000/s generation together.

## Quick start

### 1) Generate random addresses

```bash
python3 src/random_address_generator.py --type mixed --count 20
python3 src/random_address_generator.py --type ipv4 --count 1000 --output outputs/ipv4.txt
```

### 2) Run at 100000 calls per second

```bash
python3 scripts/run_100k_per_second.py --rate 100000 --seconds 3 --type mixed
```

### 3) Packet sniffing (requires root)

```bash
sudo python3 src/packet_sniffer.py --interface any --duration 5 --output outputs/packets.jsonl
```

Or capture fixed number of packets:

```bash
sudo python3 src/packet_sniffer.py --interface any --max-packets 200 --output outputs/packets.jsonl
```

### 4) Run both together (capture + generation)

```bash
python3 scripts/run_capture_and_generate.py --interface any --duration 5 --rate 100000 --seconds 5 --type mixed
```

## Notes

- Packet capture uses `AF_PACKET` raw sockets, Linux only.
- Root privileges are required for capture.
- The 100000/s target is "best-effort"; actual rate depends on CPU and environment.
