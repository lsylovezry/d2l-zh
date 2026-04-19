# 抓包程序 + 随机地址生成器：执行计划（v0）

## 1. Background
- 需求是快速实现一个可运行工具，包含抓包和随机地址生成两个模块，并支持每秒 100000 次高频执行。
- 关键限制：抓包需要系统权限（raw socket），高频执行需要轻量逻辑避免明显性能瓶颈。

## 2. Core Hypothesis
- 使用 Python 原生实现（`socket.AF_PACKET` + `random.getrandbits`）可在 Linux 上快速完成 MVP。
- 地址生成的核心循环足够轻量，可达到或接近 100000 次/秒目标（取决于硬件）。

## 3. Objectives
- 提供可直接运行的程序，默认 `--rate=100000`。
- 输出真实吞吐统计，验证是否达到目标速率。
- 抓包部分至少返回基础样本（时间戳、长度、来源）。

## 4. Task Definition
- 输入：
  - 运行参数：`rate`、`seconds`、`interface`、`public_only`。
- 输出：
  - 地址生成总量和实际速率；
  - 最近若干地址样本；
  - 抓包样本（若权限允许）。

## 5. Method Design
- 随机地址生成：32-bit 随机数映射为 IPv4 字符串。
- 高频调度：以“每秒一批”的方式执行 `rate` 次生成，若提前完成则 sleep 到 1 秒。
- 抓包：非阻塞 raw socket + `select` 轮询，在固定窗口内抓取少量样本。

## 6. Implementation Plan
- `src/random_address_generator.py`: 地址生成类。
- `src/packet_sniffer.py`: 抓包类与样本结构。
- `scripts/run_100k_per_second.py`: 主脚本，整合两个模块并打印统计。
- `README.md`: 使用说明。

## 7. Evaluation
- 运行命令：
  - `python3 scripts/run_100k_per_second.py --rate 100000 --seconds 2`
- 验证项：
  - 无报错执行；
  - 输出吞吐率；
  - 有权限时输出抓包样本，无权限时给出告警并优雅退出。

## 8. Risks
- 未使用 root 时抓包会失败（已通过异常处理降级）。
- 在低性能机器上可能达不到目标速率（脚本会报告实际值）。

## 9. Minimum Viable Experiment
- 执行 2 秒生成 + 1 秒抓包样本窗口。
- 若生成速率可观且程序稳定，MVP 完成。

## 10. Assumptions and Uncertainties
- 假设运行环境为 Linux 且 Python 版本 >= 3.10。
- 假设使用者拥有合法授权网络环境，允许进行抓包测试。
- 当前仓库中未发现 `/moban.md` 模板文件，故本计划采用可执行 v0 结构；若后续提供模板，可按模板补齐字段。
