## packet_capture_random_address

This project provides:

1. A Linux packet sniffer program (`src/packet_sniffer.py`)
2. A random address generator (`src/random_address_generator.py`)
3. A high-frequency runner that defaults to `100000` iterations per second (`src/high_frequency_runner.py`)

### Directory

```text
packet_capture_random_address/
  docs/
  configs/
  scripts/
  src/
  data/
  outputs/
  checkpoints/
  README.md
```

### Requirements

- Python 3.10+
- Linux system for packet capture (`AF_PACKET`)
- Root privilege is required for sniffer mode

### Usage

Run random address generator:

```bash
python3 src/random_address_generator.py --count 5
```

Run packet sniffer (capture 20 packets):

```bash
sudo python3 src/packet_sniffer.py --interface eth0 --count 20
```

Run high-frequency task loop (default 100000 iterations per second):

```bash
python3 src/high_frequency_runner.py --mode generator --duration-seconds 3 --report-every-second
```

Run both generator and sniffer in one loop:

```bash
sudo python3 src/high_frequency_runner.py --mode both --interface eth0 --duration-seconds 3 --report-every-second
```

Use helper script:

```bash
bash scripts/run_100k_per_sec.sh generator 3
```

or

```bash
bash scripts/run_100k_per_sec.sh both 3 eth0
```
