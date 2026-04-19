# packet_sniffer_random_address

一个最小可运行项目，包含：

1. 抓包程序（基于原始套接字，Linux）
2. 随机地址生成器（随机 IPv4）
3. 高频执行器（默认每秒 100000 次）

## 目录

- `src/random_address.py`: 随机 IPv4 地址生成
- `src/sniffer.py`: 抓包逻辑
- `src/rate_runner.py`: 固定速率循环执行器
- `src/main.py`: 组合入口
- `scripts/run.py`: 命令行启动脚本

## 运行方式

> 抓包通常需要 root 权限（或 `CAP_NET_RAW`）。

```bash
cd /workspace/packet_sniffer_random_address
python3 scripts/run.py --per-second 100000 --duration 5 --log-every 10000
```

参数说明：

- `--per-second`: 每秒执行次数（默认 100000）
- `--duration`: 运行秒数（默认 5）
- `--log-every`: 每处理多少次打印一次示例地址（默认 10000）
- `--iface`: 网卡名（可选）

## 注意

- 如果没有 root 权限，抓包器会自动降级为“未启用抓包”模式，但随机地址生成与高频调度仍会执行。
- 每秒 100000 次依赖机器性能；脚本会打印实际吞吐和误差。
- 抓包结果默认写入 `outputs/packets.log`。
