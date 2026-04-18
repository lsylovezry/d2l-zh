# packet_stress_tools

抓包程序与随机地址生成器，支持按目标速率（默认每秒 100000 次）发送 UDP 包。

## 目录

- `src/packet_stress_tools/packet_capture.py`：UDP 抓包（监听接收并统计速率）。
- `src/packet_stress_tools/random_address.py`：随机 IPv4 地址生成器。
- `src/packet_stress_tools/sender.py`：高频 UDP 发送器（可设目标 PPS）。
- `scripts/capture_udp.py`：抓包命令行程序。
- `scripts/random_address_generator.py`：随机地址命令行程序。
- `scripts/run_100k_per_sec.py`：以默认 `100000` 次/秒运行发送器。

## 快速开始

在仓库根目录执行：

```bash
python3 packet_stress_tools/scripts/capture_udp.py --host 127.0.0.1 --port 9999 --duration-seconds 3
```

另一个终端执行：

```bash
python3 packet_stress_tools/scripts/run_100k_per_sec.py --host 127.0.0.1 --port 9999 --duration 3 --pps 100000
```

随机地址生成：

```bash
python3 packet_stress_tools/scripts/random_address_generator.py --count 20
python3 packet_stress_tools/scripts/random_address_generator.py --count 20 --loopback-only
```

## 说明

- `100000` 次/秒是目标值（best effort），实际值受 Python 运行时、内核调度与硬件性能影响。
- 默认发送到 `127.0.0.1`，便于本机测试。
- 若使用 `--random-destination`，每个包都会生成一个新地址；默认限制在 `127.0.0.0/8`。
