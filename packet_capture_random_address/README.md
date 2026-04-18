# packet_capture_random_address

Simple Linux tools that provide:

1. A packet capture program (raw socket based).
2. A random address generator.
3. A combined runner that targets 100000 operations per second.

## Structure

- `scripts/packet_sniffer.py`: packet capture program.
- `scripts/random_address_runner.py`: random address generator at target rate.
- `scripts/run_both.py`: run capture and generation together.
- `src/packet_capture_random_address/*`: core implementation.

## Requirements

- Linux (for `AF_PACKET` raw socket).
- Python 3.10+ (tested with Python 3.12).
- Root privilege for packet capture (`sudo`) because raw sockets are used.

## Usage

Run from project root:

```bash
cd /workspace/packet_capture_random_address
```

### 1) Packet capture

```bash
sudo python3 scripts/packet_sniffer.py \
  --interface lo \
  --count 200 \
  --timeout 10 \
  --output outputs/packets.jsonl
```

### 2) Random address generator (100000/s)

```bash
python3 scripts/random_address_runner.py \
  --rate 100000 \
  --duration 1 \
  --loopback-only \
  --output outputs/generated_addresses.jsonl
```

### 3) Run both together

```bash
sudo python3 scripts/run_both.py \
  --rate 100000 \
  --duration 1 \
  --interface lo \
  --capture-count 5000 \
  --capture-timeout 5 \
  --loopback-only \
  --addresses-output outputs/generated_addresses.jsonl \
  --packets-output outputs/packets.jsonl
```

## Notes

- The generator uses batch scheduling to approximate high-frequency execution.
- Actual achieved rate depends on CPU and I/O speed.
- Default settings write every generated address to disk, which can reduce throughput. For higher throughput, consider buffering or shorter duration.
