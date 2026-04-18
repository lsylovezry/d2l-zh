# packet_capture_random_address

抓包程序 + 随机地址生成器，支持速率控制（默认目标：100000 次/秒）。

## 目录结构

- `src/packet_capture_random_address/random_address.py`：随机 IPv4/IPv6/MAC/主机名/端口生成
- `src/packet_capture_random_address/packet_capture.py`：Linux 原始套接字抓包
- `src/packet_capture_random_address/runner.py`：按目标 QPS 执行循环
- `scripts/run_100k_per_sec.sh`：一键按 100000 次/秒运行

## 快速开始

### 1) 仅压测生成器 + 速率控制（无需 root）

```bash
./scripts/run_100k_per_sec.sh 3 --dry-run
```

### 2) 开启真实抓包（需要 root 或 CAP_NET_RAW）

```bash
sudo ./scripts/run_100k_per_sec.sh 3 --iface eth0
```

> 若网卡名不同，请替换 `eth0`。

## 运行参数

- `--rate`：目标每秒迭代次数（默认 `100000`）
- `--duration`：运行秒数（默认 `3`）
- `--iface`：抓包网卡（默认 `any`）
- `--dry-run`：只做随机地址生成，不抓包

## 输出示例

```text
iterations=300018 elapsed=3.0002s throughput=99994.0/s
```

