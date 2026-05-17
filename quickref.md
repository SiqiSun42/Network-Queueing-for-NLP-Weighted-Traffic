# 快速参考指南

## 目录结构说明

```
Network Queueing for NLP-Weighted Traffic/
├── 核心算法
│   ├── packet.py              数据包（ID, 权重, 内容, 到达时间）
│   ├── traffic.py             泊松流量生成器
│   ├── maxweight_scheduler.py  Max-Weight 调度器 ⭐
│   └── num_scheduler.py        NUM 调度器 ⭐
│
├── 仿真框架
│   └── network_sim.py          离散时间仿真环境
│
├── 实验
│   └── run_experiment.py       实验脚本（单场景/多场景）
│
└── 文档
    ├── README.md               完整文档
    ├── PROGRESS.md             进展报告 ✨
    ├── NEXT_STEPS.md           下一步指南 ✨
    └── quickref.md             本文件
```

---

## 关键概念

### Packet（数据包）
```python
Packet(
    packet_id=1,           # 唯一ID
    weight=0.8,            # 语义重要性权重（0-1）
    content="...",         # 包的实际内容
    arrival_time=10,       # 到达时刻
    size=1                 # 包大小
)
```

### 调度算法的核心区别

| 项目 | Max-Weight | NUM |
|------|-----------|-----|
| **核心思想** | 实时动态 | 全局优化 |
| **优先级计算** | `Q(t) × w` | 静态速率分配 |
| **队列特性** | 较长（可控） | 较短（稳定） |
| **权重敏感度** | 高（根据权重调整） | 低（按类别分配） |
| **拥塞适应** | 极佳（最优异 +15%） | 一般（±3%） |

### 关键性能指标

1. **加权吞吐量** = 每时刻转发包的权重和
   - 越高越好（表示"有用信息"通过量大）
   
2. **丢包率** = 丢弃包数 / 总到达包数
   - 越低越好
   
3. **队列长度** = 当前等待的包数
   - 影响延迟（权衡指标）

4. **队列权重积压** = 队列中所有包的权重和
   - 反映重要信息堆积情况

---

## 快速操作

### 运行实验
```bash
# 1. 进入项目目录
cd "/Users/siqisun/学习/3.研一Spring/3.Advanced Communication Networks/Project/Network Queueing for NLP-Weighted Traffic/"

# 2. 运行单个基准测试（2秒）
python3 run_experiment.py
# → 按 Enter 确认

# 3. 或运行 4 场景对比（10秒）
echo "2" | python3 run_experiment.py
```

### 修改参数
编辑 `run_experiment.py`：

```python
# 第一阶段实验参数（第 9-15 行）
link_capacity = 50      # 链路容量（包/时刻）
arrival_rate = 60       # 泊松到达率
sim_time = 500          # 仿真时长
weight_dist = "bimodal" # 权重分布类型

# 权重分布选项
# - "uniform":   均匀 [0.1, 1.0]
# - "normal":    正态分布
# - "bimodal":   双峰（推荐） → 30% 重要 + 70% 不重要
```

### 查看结果
```bash
# 仿真完后自动打印：
# 1. 每 100 时刻的进度
# 2. 最终摘要（总丢包数、平均吞吐量等）
# 3. 对比结果
```

---

## 理解输出

### 标准输出示例

```
运行 Max-Weight 调度器仿真...
  时刻 100/500 - 队列长度: 200 - 丢包数: 855
  时刻 200/500 - 队列长度: 200 - 丢包数: 1902
  ...
  
Max-Weight 调度器:
  总到达包数: 30242
  总转发包数: 24997        ← 成功发送的包
  总丢弃包数: 5048         ← 被丢弃的包
  丢包率: 16.69%
  平均加权吞吐量: 31.3975  ← ⭐ 最重要！

NUM 调度器:
  ...
  
➜ Max-Weight 加权吞吐量优势: +8.14%  ← ⭐ 最终对比
```

### 如何解读

- **加权吞吐量 > 5 以上差异** → 算法明显优于对方
- **丢包率接近** → 两者都达到链路容量限制
- **队列长度差异大** → 一个重视速度，一个重视稳定

---

## 代码修改指南

### 添加新的权重分布

编辑 `traffic.py` 中的 `_generate_weight()` 函数：

```python
def _generate_weight(self) -> float:
    """生成单个包的权重"""
    if self.weight_dist == "your_custom":
        # 你的权重生成逻辑
        return random.uniform(0.2, 0.9)
    # ...其他分布
```

### 修改调度器

例如修改 Max-Weight 的队列大小限制：

编辑 `maxweight_scheduler.py` 第 35 行：
```python
max_queue_size = self.link_capacity * 5  # 修改这个系数
```

### 添加新的调度算法

创建新文件 `fair_scheduler.py`：

```python
class FairScheduler:
    def __init__(self, link_capacity: int):
        self.link_capacity = link_capacity
        self.queue = deque()
        
    def enqueue(self, packets):
        self.queue.extend(packets)
        
    def schedule(self):
        # 实现你的调度逻辑
        transmitted = []
        # ...
        return transmitted
```

然后在 `network_sim.py` 中添加对应的 `run_fair()` 方法。

---

## 常见问题排查

### Q: 运行时出错 `ModuleNotFoundError: No module named 'xxx'`

**A:**
```bash
python3 -m pip install --user -r requirements.txt
```

### Q: 队列长度一直在 0

**A:** 这通常表示到达率太低。尝试：
```python
link_capacity = 50
arrival_rate = 100  # 改大一点，制造拥塞
```

### Q: 丢包率为 0

**A:** 调度器没有主动丢包。检查代码中的 `max_queue_size`：
```python
max_queue_size = self.link_capacity * 5  # 太大了，改小点
max_queue_size = self.link_capacity * 2  # 改成这样试试
```

### Q: 两个算法性能完全一样

**A:** 可能是权重都差不多。用 `"bimodal"` 权重分布试试，会看到明显差异。

---

## 下一步任务清单

当你准备进入第二阶段时：

- [ ] 理解当前仿真的所有参数
- [ ] 能够独立修改参数并运行实验
- [ ] 能够理解和解释实验结果
- [ ] 理解 Max-Weight 和 NUM 的根本区别
- [ ] 思考如何集成真实 NLP 权重

---

## 论文写作提示

### 第一章：背景和动机
- 从 proposal.md 的"背景"部分开始
- 指出传统网络不考虑应用层语义

### 第二章：相关工作
- 提案中的三篇论文
- 补充一些经典排队论文（Lyapunov, NUM 等）

### 第三章：系统模型
- Packet 的定义
- Poisson 流量模型
- 两个调度器的数学描述

### 第四章：仿真实验
- 当前的 4 个场景
- 关键发现（Max-Weight 在重度拥塞下优 +14.83%）

### 第五章：真实文本实验
- 后续集成 NLP 权重的结果
- Task Success Rate 评估

### 第六章：结论和未来工作

---

## 性能基准

在典型配置下：

| 场景 | 运行时间 | 仿真时刻 | 性能 |
|------|---------|--------|------|
| 轻度拥塞 | 2.3s | 500 | 顺畅 |
| 4 场景对比 | 9.8s | 2000 | 可接受 |
| 1000 时刻 | 4.5s | 1000 | 仍可接受 |

**优化空间**：
- 用 Cython 加速关键路径
- 向量化某些操作
- 但当前 Python 已足够快

---

## 资源推荐阅读

关于排队论和调度：
- Lyapunov Drift 理论：Neely 的经典教材
- Network Utility Maximization：Boyd & Vandenberghe
- 当前论文中的三篇引用

关于语义通信：
- Proposal.md 中的三篇论文
- 搜索关键词：semantic communication, task-oriented networks

---

## 版本历史

**v0.1（当前）** - 2026-05-17
- 初版框架完成
- 两个算法可对比
- 4 个场景对比

**v0.2（计划）**
- 集成真实 NLP 权重

**v1.0（目标）**
- 完整论文版本
- 包含 RAG 语义补全

---

**最后：保持代码整洁，写好注释，为论文做准备！** 🎯
