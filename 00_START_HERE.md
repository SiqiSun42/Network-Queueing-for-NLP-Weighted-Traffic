# 🎯 从这里开始

欢迎来到《网络排队的语义权重流量对比分析》项目！

## 五分钟快速入门

### 1. 看看有什么（打开这个）

首先理解项目的两个核心调度器：

```
Max-Weight 调度器 (Lyapunov 漂移)
├─ 特点：实时动态，根据队列长度实时调整
├─ 公式：priority = queue_length × packet_weight
└─ 结果：在极限拥塞下性能最优 (+14.83%)

NUM 调度器 (凸优化)
├─ 特点：全局最优，静态速率分配
├─ 公式：最大化 log 效用，求解最优速率
└─ 结果：队列稳定但不适应动态变化
```

### 2. 快速验证（运行这个）

```bash
cd "/Users/siqisun/学习/3.研一Spring/3.Advanced Communication Networks/Project/Network Queueing for NLP-Weighted Traffic/"

# 方式一：基准测试（2 秒）
python3 run_experiment.py
# → 按 Enter

# 方式二：完整对比（10 秒）  
echo "2" | python3 run_experiment.py
```

你会看到：
```
Max-Weight 加权吞吐量: 31.36  ✨
NUM 加权吞吐量:        28.75

➜ Max-Weight 优势: +9.07%  ← 成功！
```

### 3. 理解结果（读这个）

- **轻度拥塞** (λ=60): Max-Weight +9.07%
- **中度拥塞** (λ=75): Max-Weight +3.12%  
- **重度拥塞** (λ=100): Max-Weight +14.83% ⭐ 最大差异！

**核心洞察**：权重分布差异越大，Max-Weight 的动态优势越明显。

---

## 项目结构导览

```
├─ 📖 文档（从这里开始读）
│  ├─ 00_START_HERE.md      ← 你在这里
│  ├─ README.md             ← 完整文档
│  ├─ NEXT_STEPS.md         ← 下一步怎么做
│  ├─ quickref.md           ← 快速参考
│  └─ PROGRESS.md           ← 进度报告
│
├─ 🔧 核心代码（~800 行）
│  ├─ packet.py             数据包结构
│  ├─ traffic.py            泊松流量生成
│  ├─ maxweight_scheduler.py Max-Weight 算法 ⭐
│  ├─ num_scheduler.py       NUM 算法 ⭐
│  └─ network_sim.py         仿真环境
│
├─ 🧪 实验
│  └─ run_experiment.py     实验脚本
│
└─ 📋 配置
   ├─ requirements.txt      依赖（只需 matplotlib）
   └─ proposal.md          原始提案
```

---

## 你需要知道的三件事

### 1. 为什么要做这个项目？

传统网络排队（FIFO、Drop-Tail）对所有包一视同仁。但在**语义通信**时代：
- 某些包更"重要"（如核心指令）
- 某些包可以丢（如修饰语）

问题：**在极度拥塞下，如何分配有限带宽来最大化"有用信息通过量"？**

### 2. 这个项目的创新点是什么？

大多数语义通信研究关注**应用层编码**。

**本项目创新**：把焦点放在**底层调度算法**，比较两种经典方法：

| 方面 | Max-Weight | NUM |
|------|-----------|-----|
| 时间特性 | 动态 | 静态 |
| 计算方式 | 贪心 | 凸优化 |
| 适应性 | 高（+15%） | 低（稳定） |

### 3. 下一步是什么？

**当前**：用随机权重验证理论  
**下一步**：用真实 NLP 权重（4-6 小时）  
**最后**：加入 RAG 语义补全，评估真实任务成功率（8-12 小时）

---

## 一分钟理解两个算法

### Max-Weight（推荐在有权重差异时使用）

```python
每个时刻：
  1. 计算所有包的优先级 = 队列长度 × 权重
  2. 优先发送高优先级的包
  3. 自动主动丢弃低权重包控制队列
  
→ 结果：队列稳定，高权重包优先通过，低权重包多被丢
```

**例子**：
```
队列中有 5 个包，链路容量只能发 2 个
W1(权重0.9) W2(0.8) W3(0.1) W4(0.1) W5(0.05)

优先级 = Q × w = 5 × [0.9, 0.8, 0.1, 0.1, 0.05]
排序后 = [4.5, 4.0, 0.5, 0.5, 0.25]

→ 发送 W1 和 W2（高权重）
→ 如需要，丢弃 W5（最低权重）
```

### NUM（推荐在需要全局最优时使用）

```python
优化问题：
  最大化：2×log(r_高) + log(r_低)  （加权效用）
  约束：r_高 + r_低 ≤ 50（链路容量）
  
求解 → 最优分配: r_高 = 33.3, r_低 = 16.7

每个时刻：
  按这个比例分配容量
  不会主动丢包，让队列自然控制
```

**例子**：
```
链路容量 50 包/时刻
最优分配：高优先级 33 包，低优先级 17 包

→ 每时刻都按这个比例发送
→ 如果高优先级只有 20 个，剩余 13 个容量浪费
→ 队列自然维持在某个长度
```

---

## 关键概念速查

| 术语 | 解释 | 重要性 |
|------|------|--------|
| **加权吞吐量** | 每时刻发送的包的权重和 | ⭐⭐⭐ 核心指标 |
| **丢包率** | 丢弃包 / 总包数 | ⭐⭐ 基础指标 |
| **队列长度** | 当前等待的包数 | ⭐⭐ 延迟指标 |
| **权重积压** | 队列中包的权重和 | ⭐ 诊断用 |
| **Lyapunov 漂移** | Max-Weight 的理论基础 | ⭐⭐⭐ 理论支撑 |
| **凸优化** | NUM 的求解方法 | ⭐⭐⭐ 理论支撑 |

---

## 快速检查清单

完成这个检查清单，说明你已准备好进入第二阶段：

- [ ] 能运行 `python3 run_experiment.py`
- [ ] 理解输出中"加权吞吐量"是最重要的指标
- [ ] 知道 Max-Weight 在重度拥塞下优势最大（+14.83%）
- [ ] 能修改 `run_experiment.py` 中的参数并重新实验
- [ ] 理解为什么权重分布很重要
- [ ] 阅读过 NEXT_STEPS.md

完成？🎉 那就可以开始第二阶段了！

---

## 第二阶段预告

### Priority 2：集成真实 NLP 权重

```python
# 今天的做法（随机权重）
weight = random.uniform(0.1, 1.0)

# 下一步（真实 NLP 权重）
nlp_score = analyze_semantic_importance(text)
# 核心动词 → 0.9
# 主要对象 → 0.8
# 修饰语 → 0.3
# 冠词 → 0.1
```

**收益**：
- 证明算法在真实文本中有效
- 更有说服力的论文

**时间**：4-6 小时

### Priority 3：RAG 语义补全

```python
# 接收端：用幸存片段补全缺失部分
received_fragments = [W1, W2, W5]  # 其他被丢了
reconstructed = rag_model.complete(received_fragments)

# 评估
tsr = task_success_rate(original, reconstructed)
# TSR 而非丢包率！
```

**收益**：
- 最终评估指标更真实
- 完整的故事线

**时间**：8-12 小时

---

## 一句话总结

> 在语义通信中，**动态调度（Max-Weight）比静态优化（NUM）更能适应权重多样化的突发流量，特别是在极限拥塞下可获得 15% 的性能提升。**

---

## 需要帮助？

### 问题 1：代码跑不起来

```bash
# 尝试这个
python3 -m pip install --user -r requirements.txt
python3 run_experiment.py
```

### 问题 2：不理解某个算法

→ 打开对应的 `.py` 文件，代码里有详细注释

### 问题 3：想修改某个参数

→ 见 `quickref.md` 的"快速操作"部分

### 问题 4：想知道下一步该做什么

→ 读 `NEXT_STEPS.md`

---

## 现在就开始吧！

```bash
cd "/Users/siqisun/学习/3.研一Spring/3.Advanced Communication Networks/Project/Network Queueing for NLP-Weighted Traffic/"
echo "2" | python3 run_experiment.py
```

看到对比结果后，打开 `NEXT_STEPS.md` 继续... 🚀

---

**祝你成功！** ✨

欢迎回到这里做第二阶段！
