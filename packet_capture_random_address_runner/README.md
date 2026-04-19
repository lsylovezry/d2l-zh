# packet_capture_random_address_runner

本项目提供两个核心能力：

1. 抓包程序（Linux raw socket）
2. 随机地址生成器（IPv4 / 私网 IPv4 / IPv6 / MAC）

并支持按目标速率执行（例如每秒 100000 次）。

## 目录结构

```text
packet_capture_random_address_runner
├── checkpoints
├── configs
├── data
├── docs
├── outputs
├── scripts
│   └── run.py
└── src
    ├── __init__.py
    ├── high_rate_runner.py
    ├── packet_sniffer.py
    └── random_address_generator.py
```

## 环境要求

- Linux
- Python 3.10+
- 抓包需要 root 权限（raw socket）

## 快速开始

### 1) 仅测试随机地址生成 + 高频执行（无需 root）

```bash
python scripts/run.py --mode generate-only --rate 100000 --duration 2
```

### 2) 抓包 + 高频执行（需要 root）

```bash
sudo python scripts/run.py --mode sniff-and-generate --interface eth0 --rate 100000 --duration 5
```

## 参数说明

- `--mode`
  - `generate-only`: 只执行随机地址生成
  - `sniff-and-generate`: 启动抓包线程并执行随机地址生成
- `--interface`: 网卡名，如 `eth0`、`ens5`
- `--rate`: 目标每秒执行次数（默认 100000）
- `--duration`: 持续秒数（默认 3）

## 注意事项

1. 每秒 100000 次在不同机器上的实际可达速率会有差异，受 CPU、内核调度和 Python GIL 影响。
2. 抓包属于系统级能力，请在合法授权环境下使用。
3. 当前实现用于学习与工程基础搭建，不包含复杂协议解析与持久化。
