# network_traffic_tools

用于**授权网络诊断/测试**的最小工具集：

- 抓包程序（被动抓取并打印摘要）
- 随机地址生成器（私有 IPv4 / 公网 IPv4 / MAC）
- 每秒 100000 次调用的吞吐基准脚本

## 目录

- `src/network_traffic_tools/packet_sniffer.py`：抓包核心
- `src/network_traffic_tools/address_generator.py`：随机地址生成核心
- `scripts/sniff_packets.py`：抓包 CLI
- `scripts/generate_random_addresses.py`：地址生成 CLI
- `scripts/run_address_generator_benchmark.py`：QPS 基准

## 快速运行

在项目根目录执行：

```bash
cd /workspace/network_traffic_tools
export PYTHONPATH=/workspace/network_traffic_tools/src
```

### 1) 随机地址生成

```bash
python scripts/generate_random_addresses.py --mode private_ipv4 --count 10
python scripts/generate_random_addresses.py --mode public_ipv4 --count 10
python scripts/generate_random_addresses.py --mode mac --count 10
```

### 2) 每秒 100000 次调用（基准）

```bash
python scripts/run_address_generator_benchmark.py --target-qps 100000 --seconds 1 --mode private_ipv4
```

输出会包含 `actual_qps`，用于确认实际吞吐。

### 3) 抓包

Linux 下通常需要 root 权限：

```bash
sudo env PYTHONPATH=/workspace/network_traffic_tools/src python scripts/sniff_packets.py --limit 20
sudo env PYTHONPATH=/workspace/network_traffic_tools/src python scripts/sniff_packets.py --interface eth0 --limit 100
```

## 安全说明

- 仅可用于你有明确授权的网络环境。
- 默认地址生成推荐 `private_ipv4` 模式，用于内网模拟。
- 该抓包程序只做被动监听和摘要输出，不包含主动攻击逻辑。
