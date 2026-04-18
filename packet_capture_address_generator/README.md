# packet_capture_address_generator

一个简单的网络工具小项目，包含：

1. 抓包程序（Linux raw socket）
2. 随机地址生成器（IPv4/IPv6/MAC）
3. 一键同时运行入口

## 目录结构

```
packet_capture_address_generator/
  docs/
  configs/
  scripts/
    run_all.sh
  src/
    packet_capture.py
    random_address_generator.py
    run_tools.py
  data/
  outputs/
  checkpoints/
  README.md
```

## 环境要求

- Linux
- Python 3.10+

抓包功能使用 `AF_PACKET` + `SOCK_RAW`，需要 root 或 `CAP_NET_RAW` 权限。

## 用法

在仓库根目录执行：

```bash
./packet_capture_address_generator/scripts/run_all.sh
```

默认行为：

- 随机地址生成器：每秒 100000 次，持续 5 秒
- 抓包：最多抓 200 个包，最多 10 秒
- 抓包日志保存到：`packet_capture_address_generator/outputs/captured_packets.log`

### 常用参数

```bash
./packet_capture_address_generator/scripts/run_all.sh \
  --rate 100000 \
  --duration 5 \
  --address-type ipv4 \
  --capture-interface eth0 \
  --capture-packet-limit 500 \
  --capture-timeout 15
```

只跑地址生成器（不抓包）：

```bash
./packet_capture_address_generator/scripts/run_all.sh --skip-capture
```

查看每秒样例输出：

```bash
./packet_capture_address_generator/scripts/run_all.sh --sample-output
```
