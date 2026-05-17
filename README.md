# Network Queueing for NLP-Weighted Traffic

## 项目概述

本项目构建一个**轻量级网络排队仿真环境**，用于对比两种调度算法在处理带语义权重的突发流量时的性能：

- **Max-Weight 调度器**：动态、实时的队列管理，基于 Lyapunov 漂移理论
- **NUM（Network Utility Maximization）调度器**：静态、全局优化的速率控制

## 第一阶段：项目骨架

当前实现包含以下模块：

### 核心组件

| 模块 | 说明 |
|------|------|
| `packet.py` | 数据包数据结构（ID、权重、到达时间） |
| `traffic.py` | 泊松流量生成器（模拟突发网络流量） |
| `maxweight_scheduler.py` | Max-Weight 调度器实现 |
| `num_scheduler.py` | NUM 调度器实现 |
| `network_sim.py` | 仿真环境（整合所有组件） |
| `run_experiment.py` | 实验脚本和可视化 |

### 工作流

```
时刻 t:
  1. 泊松过程生成到达包
  2. 包进入调度器队列
  3. 调度器做决策（转发/丢弃）
  4. 记录性能指标
  5. 重复到仿真结束
```

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行仿真

```bash
python run_experiment.py
```

### 输出

- **控制台输出**：实时仿真进度和最终摘要
- **图表**：`comparison_results.png` - 包含 4 个对比图表：
  - 队列长度演变
  - 权重积压演变
  - 累积丢包数
  - 加权吞吐量（移动平均）

## 关键参数

在 `run_experiment.py` 中调整：

```python
link_capacity = 50      # 链路容量（包/时刻）
arrival_rate = 60       # 到达速率（包/时刻）
sim_time = 500          # 仿真时长（时刻）
weight_dist = "bimodal" # 权重分布
```

- **轻度拥塞**：`arrival_rate` 略大于 `link_capacity`
- **重度拥塞**：`arrival_rate` 远大于 `link_capacity`

### 权重分布

- `"uniform"`：均匀分布 [0.1, 1.0]
- `"normal"`：正态分布
- `"bimodal"`：30% 重要 [0.8, 1.0] + 70% 不重要 [0.1, 0.3]（推荐）

## 性能指标

### 记录的指标

- **队列长度**：当前等待的包数
- **权重积压**：队列中所有包的权重总和
- **累积丢包数**：截至当前时刻被丢弃的总包数
- **加权吞吐量**：每时刻成功转发的包的权重之和
- **丢包率**：丢弃包数 / 总到达包数

## 算法说明

### Max-Weight 调度器

**原理**：Lyapunov 漂移理论

每个时刻，计算每个包的优先级：
$$\text{priority} = Q(t) \times w_i$$

其中 $Q(t)$ 是队列长度，$w_i$ 是包权重。

**优点**：
- 动态适应流量变化
- 保证队列稳定性（Lyapunov 意义）
- 自动优先转发高权重包

**缺点**：
- 不一定是全局最优

### NUM 调度器

**原理**：凸优化

将资源分配建模为凸优化问题：

$$\max \sum_i U_i(r_i)$$
$$\text{s.t.} \sum_i r_i \leq C$$

其中 $U_i(r_i) = \log(r_i)$ 是对数效用函数，$C$ 是链路容量。

**优点**：
- 全局最优解
- 理论完备

**缺点**：
- 静态分配，难以适应动态流量
- 计算复杂度高

## 后续计划

### 第二阶段：集成真实 NLP 权重

- 用 spaCy 或预训练 LLM 替代随机权重
- 从真实文本中提取语义重要性分数

### 第三阶段：加入 RAG 语义补全

- 实现接收端语义重建模块
- 评估指标从"丢包率"→"Task Success Rate"

## 文件说明

### packet.py
定义 `Packet` 数据类，表示网络中的一个数据包。

属性：
- `packet_id`: 唯一标识
- `weight`: 语义重要性权重
- `content`: 包的实际内容
- `arrival_time`: 到达时刻
- `size`: 包大小

### traffic.py
`PoissonTrafficGenerator` 生成泊松分布的突发流量。

支持的权重分布：
- `uniform`：均匀
- `normal`：正态
- `bimodal`：双峰（推荐用于语义分化）

### maxweight_scheduler.py
`MaxWeightScheduler` 实现 Max-Weight 调度算法。

调度策略：
1. 计算队列长度 × 包权重
2. 按优先级排序
3. 贪心转发最高优先级的包

### num_scheduler.py
`NUMScheduler` 使用 cvxpy 求解凸优化。

优化问题：
- 目标：最大化加权对数效用
- 约束：总速率 ≤ 链路容量
- 周期性求解并更新最优速率

### network_sim.py
`NetworkSimulator` 是仿真主体，整合所有组件。

关键方法：
- `run_maxweight()`：运行 Max-Weight 仿真
- `run_num()`：运行 NUM 仿真
- `run_both()`：对比运行两个调度器
- `print_summary()`：输出结果摘要

### run_experiment.py
实验脚本，负责：
1. 配置仿真参数
2. 运行仿真
3. 绘制对比图表

## 发展方向

1. **扩展调度器**：加入 FQ、DRR 等其他算法
2. **非泊松流量**：支持突发流模型、自相似流
3. **多链路网络**：从单链路→多跳网络
4. **真实应用**：集成 NLP + RAG，评估实际任务成功率
5. **理论分析**：推导性能上界、收敛性分析

## 参考文献

- [提案文档](proposal.md) 中提到的三篇论文
- Neely, M. J. (2010). Stochastic Network Optimization with Application to Communication and Queueing Systems.
- Boyd, S., & Vandenberghe, L. (2004). Convex Optimization.
