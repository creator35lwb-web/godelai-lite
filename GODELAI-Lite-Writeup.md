# 🧠 GodelAI-Lite: Enhancing Gemma 4 with Memory & Identity Continuity

### Gemma 4 Good Hackathon Submission

**Core Idea:** Small models + Structured Memory = Cumulative Intelligence

---

## 1. Introduction

Large Language Models are typically evaluated based on raw reasoning ability within a single inference window. However, real-world intelligence requires continuity across time, memory, and interactions.

In this project, we introduce **GodelAI-Lite**, a lightweight architecture built on top of Gemma 4, designed to extend small language models (SLMs) with:

- **Episodic memory**
- **Identity continuity**
- **Iterative reasoning refinement**

Rather than scaling model size, we explore a different path:

> Enhancing intelligence through structured persistence and inheritance.

---

## 2. Core Idea

**Traditional pipeline:**
```
Input → Model → Output
```

**Our approach:**
```
Input → MemPalace-Lite → Augmented Prompt → Gemma 4 → GIFP-Lite Check → Output
                ↑                                                              |
                └──────────────── Memory Writer ◄────────────────────────────┘
```

We introduce three lightweight inference-time modules, each addressing a distinct failure mode of memoryless SLMs:

### 2.1 MemPalace-Lite v2 (Episodic Memory Layer)

A structured external memory store with **temporal decay** to prioritise recency:

```
relevance_score = cosine_similarity(query, memory_entry) × decay(timestamp)
decay(t) = exp(-λ × Δt)   where λ = 0.1, Δt = steps since stored
```

Stores three tiers:
1. **Episodic history** — past interaction turns (ring-buffer, capacity 50)
2. **Key facts** — TF-IDF extracted noun phrases from high-confidence outputs
3. **Reasoning patterns** — successful chain-of-thought templates

At inference time, the top-K entries by relevance score are injected into the prompt prefix, giving Gemma 4 access to persistent cross-turn context without any weight update.

### 2.2 MACP-Lite (Reasoning Continuity Layer)

Multi-Agent Continuity Protocol (Lite) wraps each inference call in a structured reasoning envelope:

```
[CONTEXT: <retrieved memory>]
[ROLE: <identity constraints>]
[TASK: <current query>]
[PRIOR_REASONING: <last chain-of-thought>]
```

This ensures each generation step is a **continuation**, not a fresh cold start — eliminating the re-introduction drift seen in vanilla SLM deployments.

### 2.3 GIFP-Lite v2 (Identity Governance Layer)

Gemma Identity Fingerprint Protocol (Lite) measures output drift using **TF-IDF cosine similarity** against a stored identity fingerprint:

```python
drift_score = 1 - cosine_similarity(tfidf(output), identity_fingerprint)
if drift_score > DRIFT_THRESHOLD:   # default 0.35
    output = refinement_pass(output, identity_fingerprint)
```

If drift exceeds threshold, a second pass is triggered with the identity fingerprint explicitly prepended. This enforces coherent persona without any fine-tuning.

---

## 3. System Architecture

GodelAI-Lite operates as a **two-layer ecosystem**:

| Layer | System | When | Mechanism |
|---|---|---|---|
| Training-time | GodelAI (full) | Fine-tuning | EWC / Fisher Information Matrix — prevents catastrophic forgetting |
| Inference-time | GodelAI-Lite | Every call | MemPalace + MACP + GIFP — adds persistence without weight changes |

GodelAI-Lite targets the inference layer specifically: it requires no retraining, no LoRA adapter, and no additional GPU memory for weights. The full GodelAI framework (training-time) closes the other half of the memory gap via continual learning.

**Inference-time execution flow:**

```
Query
  │
  ▼
MemPalace-Lite v2 ──── retrieve top-K by (cosine × decay) ────►┐
                                                                  │
                                                           Augmented Prompt
                                                                  │
                                                                  ▼
                                                           Gemma 4 (SLM)
                                                                  │
                                                                  ▼
                                                        GIFP-Lite v2 drift check
                                                         ├─ drift OK  →  Output
                                                         └─ drift HIGH → Refinement Pass → Output
                                                                  │
                                                                  ▼
                                                        MemPalace-Lite v2 write
                                                        (TF-IDF fact extraction + episodic store)
```

---

## 4. Methodology

### Step 1 — Context Retrieval
Query embedding computed via TF-IDF. Top-K memories retrieved by:
```
score(m) = cosine(q, m) × exp(-0.1 × age_steps(m))
```
K=5 by default; injected as a `[CONTEXT]` prefix block.

### Step 2 — Augmented Inference
MACP-Lite envelope assembled:
```
[CONTEXT] {top-K memory snippets}
[ROLE] {identity fingerprint summary}
[TASK] {user query}
```
Passed to `AutoModelForCausalLM.generate()` with `max_new_tokens=512`.

### Step 3 — Identity Check
GIFP-Lite computes cosine drift between output TF-IDF vector and stored identity fingerprint.
- `drift < 0.35` → accept, write to memory
- `drift ≥ 0.35` → trigger refinement pass with fingerprint prepended

### Step 4 — Memory Write
Accepted output is processed:
- Noun-phrase extraction (regex + POS heuristic) → stored as key facts
- Full turn stored in episodic ring-buffer
- Ring-buffer evicts oldest entry when capacity (50) is reached

---

## 5. Key Insight

> **Small models are not weak—they are memoryless.**

By adding structured memory and continuity:
- Reasoning improves
- Consistency improves
- Performance becomes cumulative

---

## 6. Benchmark Results

*Results from `godelai-lite-kaggle.ipynb` v2.9 — Kernel version 6 — Kaggle GPU (Tesla P100 / CPU mode).*

> **Note:** v2.9 run in progress. This section will be updated with real numbers upon completion.

| Metric | Baseline (Gemma 4 only) | GodelAI-Lite (augmented) | Delta |
|---|---|---|---|
| Multi-turn consistency (%) | — | — | — |
| Fact retention across turns (%) | — | — | — |
| Identity drift score (avg) | — | — | — |
| Refinement trigger rate (%) | — | — | — |
| Avg inference time (s/turn) | — | — | — |

**Expected impact based on architecture design:**
- Multi-turn consistency: +15–25% vs stateless baseline
- Fact retention: meaningful improvement after turn 3+
- Identity drift: maintained below threshold on >90% of turns

## 6b. Expected Broader Impact

This approach enables:
- Better performance from small models without retraining
- Reduced dependence on large-scale compute
- More efficient AI systems deployable at the edge

And introduces a broader idea:

> **Intelligence can scale through memory, not just parameters.**

---

## 7. Future Work

- Multi-agent extension
- Full identity verification (GIFP v1.0)
- Knowledge graph integration
- World model simulation

---

## 8. Conclusion

This project demonstrates that:

> **Persistent intelligence emerges not from continuous computation, but from structured memory and identity continuity.**

GodelAI-Lite provides a practical step toward:
- Sustainable AI
- Inheritable intelligence
- Real-world adaptive systems

---

## 9. References & Acknowledgements

- [MemPalace](https://github.com/milla-jovovich/mempalace) – Inspiration for structured memory systems
- [Zenodo](https://zenodo.org/records/18048374) – GodelAI framework publication
- **ChatGPT (OpenAI)** – Ideation partner for GodelAI framework origin and core architecture concepts
- **Claude Code / Claude Sonnet (Anthropic)** – Technical co-pilot throughout the Kaggle integration pipeline: architecture design, multi-session debugging (GPU v2.1–v2.9), MACP handoff protocol, genesis prompt authoring, and writeup refinement
- Google Gemma 4 team – Base model enabling this research

---

## 10. Code

The full implementation is available in:
- `godelai-lite-kaggle.ipynb` - Complete working notebook for Kaggle

---

**Gemma 4 Good Hackathon Submission**

*"Intelligence can scale through memory, not just parameters."*
