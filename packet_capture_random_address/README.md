# packet_capture_random_address

This project contains:

1. A packet capture program based on Linux raw sockets.
2. A random address generator.
3. A runner that executes random address generation **100000 times per second**.

## Directory layout

```text
packet_capture_random_address/
├── docs/
├── configs/
├── scripts/
├── src/
├── data/
├── outputs/
└── checkpoints/
```

## Quick start

From `/workspace`:

```bash
python3 packet_capture_random_address/scripts/run_100k_per_sec.py --seconds 3
```

Optional packet capture mode (requires root on Linux):

```bash
sudo python3 packet_capture_random_address/scripts/run_100k_per_sec.py --seconds 3 --enable-capture --interface eth0
```

## Notes

- Raw packet capture requires root permission.
- The generator loop is configured to run 100000 iterations per second by default.
