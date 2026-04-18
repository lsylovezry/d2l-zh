# Network Packet Toolkit

这是一个最小可运行项目，包含两个核心程序：

1. 抓包程序：`src/packet_sniffer.py`
2. 随机地址生成器：`src/random_address_generator.py`

并提供高频驱动器：

- `src/high_frequency_runner.py`（将“抓包轮询 + 随机地址生成”组合运行）
- `scripts/run_100k_per_second.sh`（默认每秒 100000 次）

## 目录结构

```text
network_packet_toolkit/
├── docs/
├── scripts/
│   └── run_100k_per_second.sh
└── src/
    ├── high_frequency_runner.py
    ├── packet_sniffer.py
    └── random_address_generator.py
```

## 运行要求

- Linux 环境
- Python 3.10+
- 抓包功能使用原始套接字（`AF_PACKET`），需要 root 权限

## 使用方式

### 1) 单独运行随机地址生成器

```bash
python3 src/random_address_generator.py
```

### 2) 单独运行抓包程序

```bash
sudo python3 src/packet_sniffer.py --interface eth0 --count 10 --timeout 3
```

接口名可按机器实际情况替换，例如 `ens5` / `wlan0`。

### 3) 运行每秒 100000 次（默认 1 秒）

```bash
sudo bash scripts/run_100k_per_second.sh
```

可附加参数，比如指定网卡并延长时长：

```bash
sudo bash scripts/run_100k_per_second.sh --interface eth0 --duration-seconds 3
```

## 说明

- 高速模式中每次操作包含：
  - 一次非阻塞抓包轮询（可能读到包，也可能无包）
  - 一次随机 IPv4+端口生成
- “每秒 100000 次”按目标操作次数执行，最终会输出实际吞吐（achieved ops/s）。
