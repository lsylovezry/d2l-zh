# packet_capture_random_address

一个可执行的 Python 小项目，包含：

1. 抓包程序（基于 Linux `AF_PACKET` 原始套接字）
2. 随机地址生成器（默认生成随机 IPv4 地址）
3. 高频调度脚本（默认每秒执行 100000 次地址生成）

## 目录结构

```text
packet_capture_random_address/
├── checkpoints/
├── configs/
├── data/
├── docs/
├── outputs/
├── scripts/
│   ├── capture_packets.py
│   ├── generate_random_addresses.py
│   └── run_100k_per_second.py
└── src/
    ├── packet_sniffer.py
    └── random_address_generator.py
```

## 运行环境

- Linux
- Python 3.10+

> 抓包使用原始套接字，通常需要 root 权限或 `CAP_NET_RAW` 能力。

## 快速运行

```bash
python3 scripts/run_100k_per_second.py --rate 100000 --seconds 3 --interface any
```

单独运行随机地址生成器：

```bash
python3 scripts/generate_random_addresses.py --rate 100000 --seconds 1 --public-only
```

单独运行抓包程序（可能需要 sudo）：

```bash
sudo python3 scripts/capture_packets.py --interface any --duration 3 --sample-size 10
```

可选参数：

- `--rate`：每秒执行次数（默认 `100000`）
- `--seconds`：运行秒数（默认 `3`）
- `--interface`：抓包网卡（默认 `any`）
- `--public-only`：仅生成公网 IPv4 地址
- `--sample-size`：输出抓包样本数量（默认 `5`）

## 说明

- 本项目不会主动发送网络流量，只做本地抓包读取和地址生成。
- 请仅在你拥有授权的环境中进行抓包操作。
