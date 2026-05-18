Network Queueing for NLP-Weighted Traffic: A Comparative Analysis of NUM and Max-Weight

1\. Background

Traditional network queues (such as Drop-Tail or FIFO) treat all data packets as equivalent binary streams. When facing severe congestion, routers can only resort to indiscriminate packet dropping. However, in emerging network paradigms represented by semantic communication, traffic exhibits strong application-aware characteristics.

Specifically, by introducing a mature Natural Language Processing (NLP) framework at the sender as a preprocessing module, the internal syntax and logical relationships of the application-layer payload can be parsed. Based on their contribution to the overall task structure (for example, the weight of core action commands will be much greater than that of modifiers), different "mathematical weights" are assigned to the underlying data packets.

Motivated by this, the project aims to explore the cross-layer design of application-layer weight allocation and underlying queueing rules. Under extremely constrained bottleneck bandwidth, how should the scheduler allocate resources to maximize the overall "semantic utility" of the transmitted payload, rather than merely pursuing traditional raw bit throughput?

- Main Goals

With the rise of Large Language Models (LLMs), this field has been widely researched. However, most recent research focuses heavily on the algorithm design of the application-layer encoders. The innovation of this project lies in treating the application-layer encoder merely as a "Weighted Traffic Generator," thereby returning the research focus entirely to fundamental queueing theory.

The project will build a lightweight Python queueing simulation environment. Under bursty Poisson traffic conditions, it will contrast the theoretical trade-off between the static rate fairness of the NUM (Network Utility Maximization) framework and the dynamic queue robustness of Max-Weight scheduling through code simulations and numerical charts:

a) NUM framework: Formulates packet priority weights as a convex optimization problem to seek a static, globally optimal rate control and bandwidth allocation strategy through mathematical derivation.

b) Max-Weight scheduling based on Lyapunov drift: Employs a dynamic, real-time queue management mechanism. In each time slot, the scheduler makes per-packet drop or forward decisions based on the product of "queue backlog length \* packet weight." This ensures absolute queue stability (Lyapunov Stability) while prioritizing the throughput of high-value information.

In the implemented codebase, the receiver aggregates **successfully delivered packet payloads** (for semantic traffic, short NLP **segment texts** derived from the corpus) into a single string, ordered by packet identifier. The primary application-layer score is **Task Success Rate (TSR)**: for each of several reference corpus lines, **`weighted_similarity`** (implemented in `rag.py`) compares that line to the aggregate delivered text. This reflects how much semantically weighted content from the references survives scheduling and loss, rather than raw bit loss alone. The repository also includes an optional **RAG-style reconstructor** (`RAGReconstructor` in `rag.py`) for retrieval experiments; the default **`evaluate_rag.py`** pipeline uses the **direct aggregate–vs–reference-line** TSR above and replays the **same** stochastic arrival trace for Max-Weight and NUM within each scenario so the comparison is controlled.

- Papers to Read
- EoSI-Aware Resource Allocation for Semantic Communication-Enabled Industrial IoT System

This paper targets the semantic communication-enabled Industrial Internet of Things (SemCom-IIoT) system and proposes a novel performance metric named "efficiency of semantic information (EoSI)." When evaluating task completion, this metric comprehensively reveals the trade-off among the timeliness of semantic information, task accuracy, and resource overhead, providing a critical mathematical modeling reference for the NUM framework of this project.

- Computational Offloading in Semantic-Aware Cloud-Edge-End Collaborative Networks

This paper investigates a semantic-aware computation offloading network with cloud-edge-end collaboration. To minimize long-term energy consumption under the constraints of guaranteeing "Queue Stability" and task latency, the authors applied Lyapunov-guided optimization theory, successfully transforming the long-term stochastic optimization problem into a deterministic problem within each discrete time slot. This project will draw upon its construction equations for real task queues and virtual queues, as well as the definition method of the "Drift-Plus-Penalty" objective function, serving as the core algorithmic logic for implementing dynamic semantic real-time scheduling.

- Resource Allocation Driven by Large Models in Future Semantic-Aware Networks

This paper proposes a large-model-driven resource allocation architecture for semantic-aware networks. The authors quantitatively score the "Semantic Importance" of data fragments through pre-trained large language/vision models (such as CLIP). This project will draw upon the mechanism in this paper that utilizes large models to quantify application-layer content into an "Importance Score".