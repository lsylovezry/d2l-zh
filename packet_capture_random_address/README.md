# packet_capture_random_address

Two standalone programs are provided:

1. Packet sniffer: `src/packet_sniffer.py`
2. Random address generator: `src/random_address_generator.py`

## Environment

- Linux
- Python 3.9+

## 1) Packet sniffer

Raw socket capture requires root privileges.

Example (capture 50 TCP packets, max 15 seconds, save as JSONL):

```bash
sudo python3 src/packet_sniffer.py \
  --interface eth0 \
  --protocol tcp \
  --count 50 \
  --timeout 15 \
  --output outputs/captured_tcp.jsonl
```

Main options:

- `--interface`: interface name, `any` means all interfaces (default)
- `--protocol`: `all|tcp|udp|icmp`
- `--count`: max number of captured packets
- `--timeout`: capture timeout in seconds
- `--output`: JSONL output path (optional)

## 2) Random address generator

Default target rate is 100000 generations per second.

Run directly (5 seconds):

```bash
python3 src/random_address_generator.py --kind ipv4 --rate 100000 --duration 5
```

Save generated addresses to a file:

```bash
python3 src/random_address_generator.py \
  --kind ipv4 \
  --rate 100000 \
  --duration 5 \
  --output outputs/random_ipv4.txt
```

Main options:

- `--kind`: `ipv4|mac`
- `--rate`: target generation rate per second
- `--duration`: run duration in seconds
- `--batch-size`: batch size (default 5000)
- `--output`: output file path (optional)

## 3) One-command 100000/s run

```bash
bash scripts/run_100k_per_sec.sh
```

The script prints the measured throughput as `achieved_rate`.
