# GodelAI-Lite: Enhancing Gemma 4 with Memory & Identity Continuity

### Gemma 4 Good Hackathon Submission

[![Kaggle](https://img.shields.io/badge/Kaggle-Notebook-20BEFF?style=for-the-badge&logo=kaggle)](https://www.kaggle.com/code/creator35lwb/godelai-lite-memory-for-gemma-4)
[![Gemma](https://img.shields.io/badge/Model-Gemma_4-4285F4?style=for-the-badge)](https://ai.google.dev/gemma)
[![Version](https://img.shields.io/badge/Version-v2.9-brightgreen?style=for-the-badge)](https://github.com/creator35lwb-web/godelai-lite)
[![Status](https://img.shields.io/badge/Kernel-v6%20Running-yellow?style=for-the-badge)](https://www.kaggle.com/code/creator35lwb/godelai-lite-memory-for-gemma-4)

---

## Overview

**GodelAI-Lite** is a lightweight inference-time architecture that extends small language models (SLMs) like Gemma 4 with persistent memory, reasoning continuity, and identity governance — **without any fine-tuning or weight changes**.

> **Core Idea:** Small models are not weak — they are memoryless.

Three augmentation layers close the intelligence gap:

| Module | Role | Mechanism |
|---|---|---|
| **MemPalace-Lite v2** | Episodic memory | TF-IDF retrieval + temporal decay |
| **MACP-Lite** | Reasoning continuity | Structured prompt envelope |
| **GIFP-Lite v2** | Identity governance | Cosine drift detection + refinement |

---

## Two-Layer Ecosystem

GodelAI-Lite is the inference half of a broader two-layer architecture:

| Layer | System | When Active | Mechanism |
|---|---|---|---|
| Training-time | GodelAI (full) | Fine-tuning | EWC / Fisher Information Matrix |
| **Inference-time** | **GodelAI-Lite** | **Every call** | **MemPalace + MACP + GIFP** |

GodelAI-Lite requires no retraining, no LoRA adapter, and no additional weight memory. It installs directly on top of any pre-trained Gemma 4 checkpoint.

---

## Architecture

**Inference-time execution flow:**

```
Query
  │
  ▼
MemPalace-Lite v2 ── retrieve top-K by (cosine × decay) ──►┐
                                                              │
                                                       Augmented Prompt
                                                       [CONTEXT] [ROLE] [TASK]
                                                              │
                                                              ▼
                                                       Gemma 4 (SLM)
                                                              │
                                                              ▼
                                                   GIFP-Lite v2 drift check
                                                    ├─ drift < 0.35  →  Output
                                                    └─ drift ≥ 0.35  →  Refinement Pass → Output
                                                              │
                                                              ▼
                                                   MemPalace-Lite v2 write
                                                   (fact extraction + episodic store)
```

**MemPalace-Lite v2 — relevance scoring:**
```
score(m) = cosine_similarity(query, memory_entry) × exp(-0.1 × age_steps)
```

**GIFP-Lite v2 — identity drift:**
```
drift = 1 - cosine_similarity(tfidf(output), identity_fingerprint)
```

---

## Quick Start

### Run on Kaggle (canonical)

1. Open: [godelai-lite-memory-for-gemma-4](https://www.kaggle.com/code/creator35lwb/godelai-lite-memory-for-gemma-4)
2. **Settings → Internet: ON** (required)
3. **Add model input → Google → Gemma 4** (required)
4. Accelerator: GPU or CPU (v2.9 auto-detects)
5. Run All

> Both Internet ON and the Gemma 4 model input are required. Missing either causes DNS failure at HuggingFace download.

### Local

```bash
pip install transformers accelerate huggingface_hub torch
# Run godelai-lite-kaggle.ipynb in Jupyter
```

---

## Repository Structure

| Path | Description |
|---|---|
| `godelai-lite-kaggle.ipynb` | Main notebook — v2.9 (Kernel v6) |
| `GODELAI-Lite-Writeup.md` | Competition writeup |
| `kernel-metadata.json` | Kaggle kernel config |
| `.rk/Rk-genesis-prompt-v1.3.md` | CTO agent genesis prompt |
| `.macp/handoff-rk-session-004.md` | Latest session handoff (Session 4) |

---

## Benchmark Results

*From `godelai-lite-kaggle.ipynb` v2.9 — Kernel v6*

| Metric | Baseline (Gemma 4) | GodelAI-Lite | Delta |
|---|---|---|---|
| Multi-turn consistency (%) | — | — | — |
| Fact retention across turns (%) | — | — | — |
| Identity drift score (avg) | — | — | — |
| Refinement trigger rate (%) | — | — | — |

> Kernel v6 run in progress. Numbers will be updated on completion.

---

## Key Insight

> **Small models are not weak — they are memoryless.**

Adding structured memory and continuity:
- Improves reasoning across multi-turn interactions
- Enforces consistent identity without retraining
- Makes performance cumulative, not flat

> **Intelligence can scale through memory, not just parameters.**

---

## Version History

| Version | Kernel | Change |
|---|---|---|
| v2.1–v2.4 | — | TPU queue; phone verification blocker |
| v2.5 | GPU01 | First GPU run; `gemma4` architecture fix |
| v2.6 | GPU02 | numpy cascade fix; markdown cell JSON fix |
| v2.7 | GPU03 | bitsandbytes removed (CUDA 12.8 incompatible) |
| v2.8 | GPU04 | P100 sm_60 identified; cpu fallback designed |
| **v2.9** | **v6** | **CPU float32 mode — works on any GPU assignment** |

---

## Future Work

- [ ] Multi-agent extension (full GodelAI protocol)
- [ ] GIFP v1.0 — full identity verification
- [ ] Knowledge graph integration
- [ ] World model simulation
- [ ] T4/A100 GPU path (sm_75+) for production inference speed

---

## References & Acknowledgements

- [MemPalace](https://github.com/milla-jovovich/mempalace) — Inspiration for structured memory systems
- [GodelAI Framework](https://zenodo.org/records/18048374) — Full framework publication (Zenodo)
- [Google Gemma 4](https://huggingface.co/google) — Base model
- **ChatGPT (OpenAI)** — Ideation partner for GodelAI framework origin and core architecture concepts
- **Claude Code / Claude Sonnet (Anthropic)** — Technical co-pilot for architecture design, multi-session debugging, MACP protocol, and writeup refinement

---

## Author

**Kaggle:** [creator35lwb](https://www.kaggle.com/creator35lwb)  
**Competition:** [Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon)

---

*"Intelligence can scale through memory, not just parameters."*
