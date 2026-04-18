# packet_address_runner

一个最小可运行项目，包含：

1. 抓包程序（Linux 原始套接字）
2. 随机地址生成器（IPv4 / 私网 IPv4 / MAC / URL）
3. 压力运行器（按秒执行，默认每秒 100000 次）

## 目录

```text
packet_address_runner/
  docs/
  configs/
  scripts/
    run_100k_per_sec.sh
  src/
    packet_sniffer.py
    random_address_generator.py
    stress_runner.py
```

## 环境要求

- Linux
- Python 3.8+
- 抓包需要 root 权限或 sudo

## 1) 随机地址生成器

示例：

```bash
python3 src/random_address_generator.py --type ipv4 --count 5
python3 src/random_address_generator.py --type private_ipv4 --count 5
python3 src/random_address_generator.py --type mac --count 5
python3 src/random_address_generator.py --type url --count 5
```

## 2) 抓包程序

示例（监听全部网卡 5 秒，最多抓 20 个包）：

```bash
sudo python3 src/packet_sniffer.py --interface any --duration 5 --count 20
```

监听指定网卡（例如 eth0）：

```bash
sudo python3 src/packet_sniffer.py --interface eth0 --duration 10 --count 100
```

## 3) 每秒运行 100000 次

默认执行 5 轮（每轮 1 秒），每轮目标 100000 次：

```bash
./scripts/run_100k_per_sec.sh
```

也可以通过环境变量覆盖参数：

```bash
RATE=100000 SECONDS=10 ADDRESS_TYPE=mac ./scripts/run_100k_per_sec.sh
```

或直接运行：

```bash
python3 src/stress_runner.py --rate 100000 --seconds 10 --type ipv4
```
