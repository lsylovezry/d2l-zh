# network_packet_tools 使用说明

本目录包含两个程序：

1. 抓包程序：`src/packet_sniffer.py`
2. 随机地址生成器：`src/random_address_generator.py`

以及一个高频运行脚本：

- `scripts/run_address_generator_100k.py`（默认每秒执行 100000 次）

## 1) 抓包程序

Linux 下使用原始套接字抓取网络包，输出简要摘要（时间、长度、源地址、目的地址、协议）。

### 运行示例

```bash
cd /workspace/network_packet_tools
sudo python3 src/packet_sniffer.py --interface eth0 --count 100 --timeout 30
```

如果希望保存输出：

```bash
sudo python3 src/packet_sniffer.py --interface eth0 --count 200 --timeout 60 --output outputs/sniff.log
```

说明：
- 抓包通常需要 root 权限。
- 接口名需要按机器实际情况调整（例如 `eth0`、`ens5`、`lo`）。

## 2) 随机地址生成器

支持模式：
- `ipv4`
- `ipv6`
- `mac`
- `socket`（ip:port）
- `url`

### 运行示例

```bash
cd /workspace/network_packet_tools
python3 src/random_address_generator.py --mode ipv4 --count 20
python3 src/random_address_generator.py --mode mac --count 20
python3 src/random_address_generator.py --mode url --count 10
```

## 3) 每秒运行 100000 次

默认就是每秒 100000 次：

```bash
cd /workspace/network_packet_tools
python3 scripts/run_address_generator_100k.py --mode ipv4 --seconds 10
```

自定义速率：

```bash
python3 scripts/run_address_generator_100k.py --mode socket --target-per-sec 100000 --seconds 30
```

脚本每秒打印状态：
- `on-target`：本秒生成完成并成功补齐等待到 1 秒
- `overloaded`：本秒生成耗时超过 1 秒，机器性能不足以达到目标速率
