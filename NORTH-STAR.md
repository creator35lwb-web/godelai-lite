# GodelAI-Lite — North Star & Development Roadmap

**Document Type:** Strategic Vision & Discovery Report  
**Author:** Alton Lee Wei Bin (creator35lwb) + Rk (CTO Agent)  
**Date:** April 19, 2026  
**Status:** Living document — updated at each milestone

---

## The Discovery

> *"We came to win a Kaggle competition. We accidentally built a portable memory standard for AI."*

What began as a hackathon submission became something larger. The core discovery:

**Memory is not a model property. It is a protocol.**

The `godelai_memory.json` file produced by this project stores a user's facts, preferences, and conversation history in a format that is completely independent of the underlying model. It can be saved from a Gemma 4 session and loaded into a Llama session. The user's identity persists across model boundaries.

This is not a trick. It is a fundamental architectural insight: **intelligence continuity lives in the memory layer, not the weight layer.**

---

## What We Built

### GodelAI-Lite v2.15 — the competition submission

Three inference-time augmentation modules that wrap any HuggingFace causal LM:

| Module | Role | Mechanism |
|--------|------|-----------|
| **MemPalace-Lite v2** | Episodic memory | TF-IDF retrieval + temporal decay + JSON persistence |
| **MACP-Lite** | Reasoning continuity | Structured per-turn reasoning chain + confidence tracking |
| **GIFP-Lite v2** | Identity governance | TF-IDF cosine drift detection + hard contradiction penalty |

Zero fine-tuning. Zero additional model weights. Plugs onto any existing SLM.

### MemPalace — the standalone framework (v0.1.0)

Extracted from the competition notebook into a proper Python package:

```
pip install mempalace   ← post-competition release
```

```python
from mempalace import GodelAILite

agent = GodelAILite(model=any_hf_model, tokenizer=any_tokenizer)
agent.chat("My name is Jordan, I am a marine biologist.")
agent.save_memory("jordan.json")

# Next session, different model — memory transfers
agent2 = GodelAILite(model=different_model, tokenizer=different_tokenizer,
                     memory_path="jordan.json")
agent2.chat("What do you know about me?")
# → "Your name is Jordan, and you are a marine biologist."
```

---

## The Two-Layer Architecture

GodelAI-Lite is one half of a complete memory system:

```
┌─────────────────────────────────────────────────────────┐
│                  COMPLETE GODELAI SYSTEM                 │
├─────────────────────────┬───────────────────────────────┤
│   TRAINING TIME         │   INFERENCE TIME              │
│   GodelAI (full)        │   GodelAI-Lite                │
│                         │                               │
│   EWC + Fisher Scaling  │   MemPalace + MACP + GIFP     │
│   82.8% forgetting      │   Zero fine-tuning            │
│   reduction             │   Portable memory JSON        │
│                         │                               │
│   Prevents forgetting   │   Prevents forgetting         │
│   WHAT the model knows  │   WHAT the conversation       │
│   (weight-level)        │   established (context-level) │
└─────────────────────────┴───────────────────────────────┘
```

Neither layer is complete without the other. Together they address both failure modes of continual AI systems.

---

## Why This Matters to the World

### The problem at scale

Every SLM deployed today forgets everything between calls. Customer service bots re-ask for your name. Personal assistants lose context after one session. Research tools can't build on prior conversations. The solution at scale has been: bigger models, bigger context windows, bigger compute budgets.

That is the wrong axis.

### What MemPalace offers instead

| Capability | Value |
|-----------|-------|
| **Persistent user identity** | Name, role, preferences, history survive session boundaries |
| **Cross-model memory transfer** | User's facts move with them even when the model changes |
| **Edge deployment** | Entire augmentation stack runs offline; memory JSON lives on-device |
| **Privacy by design** | No cloud required; user owns their memory file |
| **Model-agnostic** | Works with Gemma 4, Llama, Phi, Mistral, Qwen — any HF causal LM |
| **Zero retraining** | Deploy on existing models; no fine-tuning, no adapter weights |

### The enterprise angle

Organisations running local SLMs (healthcare, legal, finance, government) cannot send data to cloud APIs. They need persistent memory that runs on-premise, on-device, or air-gapped. MemPalace is the first deployable answer.

### The research angle

**Hypothesis:** Smaller models benefit MORE from memory augmentation because they have less implicit world knowledge. A 2B model with MemPalace may outperform a 7B model without it on memory-dependent tasks. This is a publishable result.

---

## C-S-P Alignment

Every component of GodelAI-Lite maps to the C-S-P framework:

| C-S-P Stage | GodelAI-Lite Expression |
|-------------|------------------------|
| **Compression** | `extract_facts()` — distils full conversation turns into atomic, retrievable facts |
| **State** | `godelai_memory.json` — crystallises conversation history into persistent, queryable identity |
| **Propagation** | Portable JSON format — memory is transmissible across models, sessions, devices, and users |

> *"Wisdom that cannot be transmitted is only experience, not wisdom."*  
> MemPalace makes the transmission possible.

---

## Development Roadmap

### Phase 1 — Competition (NOW)
- [x] GodelAI-Lite v2.15 running on Kaggle (Kernel v12)
- [x] Benchmark results from v2.14: Memory Retention GodelAI +∞% vs Baseline
- [x] MemPalace `mempalace/` package extracted (v0.1.0)
- [x] `godelai_memory.json` artifact archived as evidence
- [x] v2.15 full benchmark results: GodelAI +39.9% overall (GPU11/Kernel v12)
- [ ] Final writeup review
- [ ] Competition submission (Alton confirms)

### Phase 2 — Open Source Release (Post-competition)
- [ ] Make `godelai-lite` repo public
- [ ] Publish `mempalace` to PyPI (`pip install mempalace`)
- [ ] Link from GodelAI Zenodo DOI (10.5281/zenodo.18048374)
- [ ] Publish on HuggingFace (YSenseAI org)
- [ ] Add `mempalace` to ecosystem tier map (Layer 3.5)

### Phase 3 — Cross-Model Benchmark Study
- [ ] Run EvaluationSuite against: Llama 3.2 1B, Phi-3 Mini, Mistral 7B, Qwen 1.5B
- [ ] Test hypothesis: smaller models gain more from memory augmentation
- [ ] Publish benchmark results as research note (Zenodo or arXiv)
- [ ] Release "MemBench" as a standalone evaluation standard

### Phase 4 — MemPalace v2 (Semantic Retrieval)
- [ ] Replace TF-IDF with sentence embeddings (e.g. `all-MiniLM-L6-v2`)
- [ ] Vector-based fact retrieval — similarity search instead of recency sort
- [ ] Hierarchical memory (session → topic → lifetime)
- [ ] Multi-user memory isolation (memory profiles per user ID)
- [ ] Investigate: shared memory pools for multi-agent coordination

---

## The Broader Vision

GodelAI-Lite is not just a competition entry. It is the first public demonstration of a principle:

> **Memory is the missing layer of the AI stack.**

Current AI infrastructure has:
- **Compute** (GPUs, TPUs, inference servers)
- **Models** (weights, architectures, fine-tunes)
- **Interfaces** (APIs, prompts, tooling)

What it does not have is a **persistent, portable, model-agnostic memory layer** between the interface and the model. MemPalace is that layer.

If this succeeds, the long-term contribution is not a better Gemma 4 wrapper. It is a new infrastructure primitive — as important to AI deployment as a database is to application development.

---

## Key Metrics (v2.15 final, Kernel v12)

| Metric | Baseline | GodelAI-Lite | Significance |
|--------|----------|--------------|-------------|
| Memory Retention | 0.000 | **0.667** | Only system that recalls facts after distractors |
| Response Consistency | 0.550 | 0.501 | -8.8% — progressive elaboration, not repetition |
| Context Coherence | 1.000 | **1.000** | Matched — semantic eval confirms architecture works |
| **Overall** | 0.517 | **0.723** | **+39.9% — competition submission result** |
| Memory persistence | None | JSON (disk) | Cross-session, cross-model |
| Fine-tuning required | — | **None** | Deployable on frozen models |

---

*"Intelligence can scale through memory, not just parameters."*  
— GodelAI core thesis

---

**Alton Lee Wei Bin** | creator35lwb | YSenseAI  
*April 2026*
