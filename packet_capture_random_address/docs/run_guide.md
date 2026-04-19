# Run Guide

## Goal

Provide two programs and execute at target frequency:

1. Packet sniffer
2. Random address generator
3. High-frequency loop at `100000` iterations per second

## Commands

### 1) Random address generator

```bash
python3 src/random_address_generator.py --count 5
```

### 2) Packet sniffer (Linux, root required)

```bash
sudo python3 src/packet_sniffer.py --interface eth0 --count 20
```

### 3) Run 100000 iterations per second

Generator only:

```bash
python3 src/high_frequency_runner.py --mode generator --iterations-per-second 100000 --duration-seconds 3 --report-every-second
```

Sniffer only:

```bash
sudo python3 src/high_frequency_runner.py --mode sniffer --interface eth0 --iterations-per-second 100000 --duration-seconds 3 --report-every-second
```

Both:

```bash
sudo python3 src/high_frequency_runner.py --mode both --interface eth0 --iterations-per-second 100000 --duration-seconds 3 --report-every-second
```

## Helper script

```bash
bash scripts/run_100k_per_sec.sh generator 3
```

or:

```bash
bash scripts/run_100k_per_sec.sh both 3 eth0
```
